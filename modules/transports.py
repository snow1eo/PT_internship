import json
import sqlite3
from abc import ABCMeta, abstractmethod
from typing import NamedTuple

import os.path
import paramiko
import pymysql
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, \
    UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

from modules.errors import TransportConnectionError, MySQLError, \
    AuthenticationError, UnknownTransport, UnknownDatabase, \
    RemoteHostCommandError, SSHFileNotFound, SNMPStatusError, \
    SNMPError

CACHE_DB_NAME = 'cache.sqlite3'
ENV_FILE = os.path.join('config', 'env.json')
_raw_conf = None
_cache = dict()


class Transport(metaclass=ABCMeta):
    def __init__(self, host, port, user, password, environment):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.env = environment
        self.conn = None
        self.connect()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @property
    @abstractmethod
    def NAME(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def remove_from_cache(self):
        global _cache
        _cache.pop(tuple([
            self.NAME,
            self.host,
            self.port,
            self.user,
            self.password]))


class MySQLTransport(Transport):
    NAME = 'MySQL'

    def connect(self, database=None):
        self.env['MYSQL_DATABASE'] = database
        try:
            self.conn = pymysql.connect(host=self.host,
                                        port=self.port,
                                        user=self.user,
                                        password=self.password,
                                        database=self.env['MYSQL_DATABASE'],
                                        charset='utf8',
                                        cursorclass=pymysql.cursors.DictCursor,
                                        unix_socket=False)
        except pymysql.err.OperationalError as e_info:
            if "Access denied" in str(e_info):
                raise AuthenticationError(self.user, self.password)
            elif "Can't connect to MySQL server" in str(e_info):
                raise TransportConnectionError(self.host, self.port)
        except pymysql.err.InternalError as e_info:
            if "Unknown database" in str(e_info):
                raise UnknownDatabase(database)
        except Exception:
            raise TransportConnectionError(self.host, self.port)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        self.remove_from_cache()

    def sqlexec(self, sql):
        with self.conn.cursor() as curr:
            try:
                curr.execute(sql)
            except Exception:
                raise MySQLError(sql)
        self.conn.commit()
        return curr.fetchall()

    def get_global_variables(self):
        with sqlite3.connect(CACHE_DB_NAME) as db:
            curr = db.cursor()
            curr.execute("SELECT name FROM sqlite_master where type = 'table'")
            tables = curr.fetchall()
            tables = list(map(list, tables))  # Converting a list
            tables = set(sum(tables, []))
            if 'variable' in tables:
                return {
                    var[0]: var[1] for var in
                    curr.execute("SELECT name, value FROM variable").fetchall()
                }
        self.connect('information_schema')
        variables = {
            var['VARIABLE_NAME']: var['VARIABLE_VALUE'] for var in
            self.sqlexec("SELECT * FROM information_schema.global_variables")
        }
        with sqlite3.connect(CACHE_DB_NAME) as db:
            curr = db.cursor()
            curr.execute("""CREATE TABLE IF NOT EXISTS variable(
                            name TEXT, value TEXT)""")
            for var in variables.items():
                curr.execute("""INSERT INTO variable VALUES (?, ?)""", var)
        return variables

    def check_vars_value(self, var, value):
        return self.get_global_variables()[var] == value

    def get_version(self):
        versions = ['9.7.3', '10.0.35', '10.2.0', '10.2.14']
        versions.sort(reverse=True)
        current_version = self.get_global_variables()['VERSION']
        for version in versions:
            if version in current_version:
                return version
        return 'not in list'


class SSHTransport(Transport):
    NAME = 'SSH'

    def connect(self):
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.conn.connect(hostname=self.host,
                              port=self.port,
                              username=self.user,
                              password=self.password)
        except paramiko.ssh_exception.AuthenticationException:
            raise AuthenticationError(self.user, self.password)
        except Exception:
            raise TransportConnectionError(self.host, self.port)

    def close(self):
        self.conn.close()
        self.remove_from_cache()

    def execute(self, command):
        stdin, stdout, stderr = self.conn.exec_command(command)
        err = stderr.read()
        if err:
            raise RemoteHostCommandError(err)
        return stdin, stdout, stderr

    def execute_show(self, command):
        return self.execute(command)[1].read().decode()

    def get_file(self, filename):
        sftp = self.conn.open_sftp()
        try:
            with sftp.open(filename) as f:
                data = f.read()
        except FileNotFoundError:
            raise SSHFileNotFound(filename)
        return data


class SNMPTransport(Transport):
    NAME = 'SNMP'

    def connect(self):
        try:
            self.conn = SnmpEngine()
        except Exception:
            raise TransportConnectionError(self.host, self.port)

    def close(self):
        self.remove_from_cache()

    def get_snmpdata(self, *oids):
        # передаю сырой oid, потому что с местными MID не смог разобраться нормально 
        result = list()
        for oid in oids:
            errorIndication, errorStatus, errorIndex, varBinds = next(
                getCmd(
                    self.conn,
                    CommunityData(self.env['community'], mpModel=0),
                    UdpTransportTarget((self.host, self.port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid)))
            )
            if errorIndication:
                raise SNMPError(errorIndication)
            elif errorStatus:
                raise SNMPStatusError(errorStatus.prettyPrint(),
                                      errorIndex and
                                      varBinds[int(errorIndex) - 1][0] or '?')
            else:
                for varBind in varBinds:
                    result.append(varBind[1].prettyPrint())
        return result


_TRANSPORTS = {
    'SSH': SSHTransport,
    'MySQL': MySQLTransport,
    'SNMP': SNMPTransport
}


class TransportConfig(NamedTuple):
    host: str
    port: int
    user: str
    password: str
    environment: dict


def _load_config():
    global _raw_conf
    if not _raw_conf:
        with open(ENV_FILE) as f:
            _raw_conf = json.load(f)


def get_transport_config(transport_name):
    _load_config()
    return TransportConfig(
        host=_raw_conf['host'],
        port=_raw_conf['transports'][transport_name]['port'],
        user=_raw_conf['transports'][transport_name]['user'],
        password=_raw_conf['transports'][transport_name]['password'],
        environment=_raw_conf['transports'][transport_name]['environment'])


def get_transport_names():
    _load_config()
    return set(_raw_conf['transports'].keys())


def get_host_name():
    _load_config()
    return _raw_conf['host']


def close_all_connections():
    for transport in tuple(_cache.values()):
        transport.close()


def get_transport(transport_name,
                  host=None,
                  port=None,
                  user=None,
                  password=None,
                  environment=None):
    if transport_name not in _TRANSPORTS:
        raise UnknownTransport(transport_name)
    config = get_transport_config(transport_name)
    host = host or config.host
    port = port or config.port
    user = user or config.user
    password = password or config.password
    environment = environment or config.environment
    args = (transport_name, host, port, user, password)
    global _cache
    if args in _cache:
        return _cache[args]
    _cache[args] = _TRANSPORTS[transport_name](
        host, port, user, password, environment)
    return _cache[args]
