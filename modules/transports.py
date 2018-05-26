import json
import sqlite3
from abc import ABCMeta, abstractmethod
from base64 import b64encode
from typing import NamedTuple

import os.path
import paramiko
import pymysql
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, ContextData, \
    UdpTransportTarget, ObjectType, ObjectIdentity

from modules.errors import TransportConnectionError, AuthenticationError, \
    UnknownTransport, RemoteHostCommandError, MySQLError, UnknownDatabase, \
    SSHFileNotFound, SNMPStatusError, SNMPError, PermissionDenied

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
                                        unix_socket=False,
                                        connect_timeout=31536000)
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

    def load_table(self, table):
        database, table = table.split('.')
        with sqlite3.connect(CACHE_DB_NAME) as db:
            curr = db.cursor()
            curr.execute("""CREATE TABLE IF NOT EXISTS database(
                            name TEXT PRIMARY KEY)""")
            curr.execute("""CREATE TABLE IF NOT EXISTS cached_table(
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            database TEXT NOT NULL,
                            data_json TEXT,
                            FOREIGN KEY (database) REFERENCES database(name))""")
            if curr.execute("SELECT name FROM database WHERE name = ?",
                            (database,)).fetchall():
                curr.execute("INSERT INTO database VALUES (?)", (database,))
            if curr.execute("""SELECT name FROM cached_table
                               WHERE database = ? AND name = ?""",
                            (database, table)).fetchall():
                return json.loads(curr.execute(
                    """SELECT data_json FROM cached_table WHERE database = ?
                       AND name = ?""", (database, table)).fetchone()[0])
            else:
                data = self.sqlexec("SELECT * FROM {}.{}".format(database, table))
                for item in data:
                    for key, value in item.items():
                        if type(value) == bytes:
                            item[key] = b64encode(value).decode()
                        else:
                            item[key] = str(value)
                curr.execute("INSERT INTO cached_table VALUES (NULL, ?, ?, ?)",
                             (table, database, json.dumps(data)))
                return data


class SSHTransport(Transport):
    NAME = 'SSH'

    def connect(self):
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.conn.connect(hostname=self.host,
                              port=self.port,
                              username=self.user,
                              password=self.password,
                              look_for_keys=False)
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
            if "Permission denied" in str(err):
                raise PermissionDenied(err)
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
