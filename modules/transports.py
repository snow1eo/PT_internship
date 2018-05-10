import json
from abc import ABCMeta, abstractmethod
from typing import NamedTuple

import os.path
import paramiko
import pymysql

from modules.wmi_client_wrapper import WmiClientWrapper
from modules.errors import TransportConnectionError, MySQLError, \
    AuthenticationError, UnknownTransport, UnknownDatabase, \
    RemoteHostCommandError, SSHFileNotFound

ENV_FILE = os.path.join('config', 'env.json')
_raw_conf = None
_cache = dict()


class Transport(metaclass=ABCMeta):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
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
        self.database = database
        try:
            self.conn = pymysql.connect(host=self.host,
                                        port=self.port,
                                        user=self.user,
                                        password=self.password,
                                        database=self.database,
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

    def get_file(self, filename):
        sftp = self.conn.open_sftp()
        try:
            with sftp.open(filename) as f:
                data = f.read()
        except FileNotFoundError:
            raise SSHFileNotFound(filename)
        return data


class WMITransport(Transport):
    NAME = 'WMI'

    # Так как используем wpapper, коннект не нужен
    def connect(self):
        pass

    def close(self):
        self.remove_from_cache()

    def wmi_exec(self, command):
        wmic = WmiClientWrapper(
            username=self.user,
            password=self.password,
            host=self.host)
        return wmic.execute(command)

    def wmi_query(self, request):
        wmic = WmiClientWrapper(
            username=self.user,
            password=self.password,
            host=self.host)
        return wmic.query(request)


# По заданию нужен отдельный транспорт, однако я думаю, можно было бы
# и в предыдущий добавить
class WMIRegistryTransport(Transport):
    NAME = 'WMIRegistry'

    # Так как используем wpapper, коннект не нужен
    def connect(self):
        pass

    def close(self):
        self.remove_from_cache()

    def get_value(self, hive, path, value_name):
        wmic = WmiClientWrapper(
            username=self.user,
            password=self.password,
            host=self.host)
        query = """SELECT * FROM RegistryValueChangeEvent WHERE
                   Hive = '{hive}' AND KeyPath = '{path}' AND
                   ValueName = '{value_name}'""".format(
                        hive=hive, path=path, value_name=value_name)
        return wmic.query(query)


_TRANSPORTS = {
    'SSH': SSHTransport,
    'MySQL': MySQLTransport,
    'WMI': WMITransport,
    'WMIRegistry': WMIRegistryTransport
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
                  password=None):
    if transport_name not in _TRANSPORTS:
        raise UnknownTransport(transport_name)
    config = get_transport_config(transport_name)
    host = host or config.host
    port = port or config.port
    user = user or config.user
    password = password or config.password
    args = (transport_name, host, port, user, password)
    global _cache
    if args in _cache:
        return _cache[args]
    _cache[args] = _TRANSPORTS[transport_name](host, port, user, password)
    return _cache[args]
