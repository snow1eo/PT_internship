import json

import os.path
import paramiko
import pymysql


class TransportError(Exception):
    pass


class TransportConnectionError(TransportError):
    pass


class AuthenticationError(TransportConnectionError):
    pass


class TransportCreationError(TransportError):
    pass


class MySQLError(TransportError):
    pass


class UnknownDatabase(TransportConnectionError):
    pass


ENV_FILE = os.path.join('config', 'env.json')
_config = None


class MySQLTransport:

    def __init__(self, host, port, login, password):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self._conn = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def connect(self, database=None):
        try:
            self._conn = pymysql.connect(host=self.host,
                                         port=self.port,
                                         user=self.login,
                                         password=self.password,
                                         db=database,
                                         charset='utf8',
                                         cursorclass=pymysql.cursors.DictCursor,
                                         unix_socket=False)
        except pymysql.err.OperationalError as e_info:
            if "Access denied" in str(e_info):
                raise AuthenticationError("Authentication failed")
            elif "Can't connect to MySQL server" in str(e_info):
                raise TransportConnectionError("Couldn't connect to host")
        except pymysql.err.InternalError as e_info:
            if "Unknown database" in str(e_info):
                raise UnknownDatabase("Unknown database")

    def sqlexec(self, sql):
        with self._conn.cursor() as curr:
            try:
                curr.execute(sql)
            except Exception as e_info:
                raise MySQLError(e_info)
            return curr.fetchall()

    def close(self):
        if self._conn:
            self._conn.close()


class SSHTransport:

    def __init__(self, host, port, login, password):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self._conn = paramiko.SSHClient()
        self._conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def connect(self):
        try:
            self._conn.connect(hostname=self.host,
                               port=self.port,
                               username=self.login,
                               password=self.password)
        except paramiko.ssh_exception.AuthenticationException:
            raise AuthenticationError('Authentication failed')
        except Exception:
            raise TransportConnectionError("Couldn't connect to host")

    def close(self):
        self._conn.close()

    def execute(self, command):
        stdin, stdout, stderr = self._conn.exec_command(command)
        err = stderr.read()
        if err:
            raise TransportError(err)
        return stdin, stdout, stderr

    def get_file(self, path):
        sftp = self._conn.open_sftp()
        try:
            with sftp.open(path) as f:
                data = f.read()
        except FileNotFoundError:
            raise TransportError('File not found')
        return data


_AVAILABLE_TRANSPORTS = {'SSH', 'MySQL'}


def get_transport(transport_name,
                  host=None,
                  port=None,
                  login=None,
                  password=None):  # Нужно же передавать для MySQL?
    if transport_name not in _AVAILABLE_TRANSPORTS:
        raise TransportCreationError('UnknownTransport')

    if host is None or port is None or\
       login is None or password is None:
        conf = get_config()
        if host is None:
            host = conf['host']
        if port is None:
            port = conf['transports'][transport_name]['port']
        if login is None:
            login = conf['transports'][transport_name]['login']
        if password is None:
            password = conf['transports'][transport_name]['password']

    if transport_name == 'SSH':
        return SSHTransport(host, port, login, password)
    elif transport_name == 'MySQL':
        return MySQLTransport(host, port, login, password)
    else:
        raise TransportCreationError('UnknownTransport')


def get_config():
    global _config
    if not _config:
        with open(ENV_FILE) as f:
            _config = json.load(f)
    return _config
