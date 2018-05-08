import json
from abc import ABCMeta, abstractmethod
from typing import NamedTuple

import os.path
import paramiko
import pymysql

from modules.errors import TransportConnectionError, MySQLError, \
    AuthenticationError, UnknownTransport, UnknownDatabase, \
    RemoteHostCommandError, SSHFileNotFound

ENV_FILE = os.path.join('config', 'env.json')
_TRANSPORT_LIST = frozenset({'SSH', 'MySQL'})
_raw_conf = None
_cache = dict()


class Transport(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, host, port, login, password):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass


class MySQLTransport(Transport):
    def __init__(self, host, port, login, password):
        self.env = dict(
            host=host,
            port=port,
            user=login,
            password=password,
            database=None)
        self.conn = None
        self.connect()

    def name(self):
        return 'MySQL'

    def connect(self, database=None):
        self.env.update(dict(database=database))
        try:
            self.conn = pymysql.connect(**self.env,
                                        charset='utf8',
                                        cursorclass=pymysql.cursors.DictCursor,
                                        unix_socket=False)
        except pymysql.err.OperationalError as e_info:
            if "Access denied" in str(e_info):
                raise AuthenticationError(self.env['user'], self.env['password'])
            elif "Can't connect to MySQL server" in str(e_info):
                raise TransportConnectionError(self.env['host'], self.env['port'])
        except pymysql.err.InternalError as e_info:
            if "Unknown database" in str(e_info):
                raise UnknownDatabase(database)
        except Exception:
            raise TransportConnectionError(self.env['host'], self.env['port'])

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
        global _cache
        _cache.pop(tuple([
            self.name(),
            self.env['host'],
            self.env['port'],
            self.env['user'],
            self.env['password']]))

    def sqlexec(self, sql):
        with self.conn.cursor() as curr:
            try:
                curr.execute(sql)
            except Exception:
                raise MySQLError(sql)
        self.conn.commit()
        return curr.fetchall()


class SSHTransport(Transport):
    def __init__(self, host, port, login, password):
        self.env = dict(
            hostname=host,
            port=port,
            username=login,
            password=password)
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect()

    def name(self):
        return 'SSH'

    def connect(self):
        try:
            self.conn.connect(**self.env)
        except paramiko.ssh_exception.AuthenticationException:
            raise AuthenticationError(self.env['username'], self.env['password'])
        except Exception:
            raise TransportConnectionError(self.env['hostname'], self.env['port'])

    def close(self):
        self.conn.close()
        global _cache
        _cache.pop(tuple([
            self.name(),
            self.env['hostname'],
            self.env['port'],
            self.env['username'],
            self.env['password']]))

    def execute(self, command):
        stdin, stdout, stderr = self.conn.exec_command(command)
        err = stderr.read()
        if err:
            raise RemoteHostCommandError(err)
        return stdin, stdout, stderr

    def get_file(self, filename):
        sftp = self.conn.open_sftp()
        try:
            with sftp.open(filename) as f:
                data = f.read()
        except FileNotFoundError:
            raise SSHFileNotFound(filename)
        return data


_TRANSPORTS = {
    'SSH': SSHTransport,
    'MySQL': MySQLTransport
    }


class TransportConfig(NamedTuple):
    host: str
    port: int
    login: str
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
            login=_raw_conf['transports'][transport_name]['login'],
            password=_raw_conf['transports'][transport_name]['password'],
            environment=_raw_conf['transports'][transport_name]['environment'])


def get_transport_names():
    _load_config()
    return set(_raw_conf['transports'].keys())


def get_host_name():
    _load_config()
    return _raw_conf['host']


def close_all_connections():
    transports = tuple(_cache.values())
    for transport in transports:
        transport.close()


def get_transport(transport_name,
                  host=None,
                  port=None,
                  login=None,
                  password=None):
    if transport_name not in _TRANSPORT_LIST:
        raise UnknownTransport(transport_name)
    config = get_transport_config(transport_name)
    host = host or config.host
    port = port or config.port
    login = login or config.login
    password = password or config.password
    args = (transport_name, host, port, login, password)
    global _cache
    if args in _cache:
        return _cache[args]
    _cache[args] = _TRANSPORTS[transport_name](host, port, login, password)
    return _cache[args]
