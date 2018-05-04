import json

import os.path
import paramiko
import pymysql

from modules.errors import TransportError, TransportConnectionError, \
    MySQLError, AuthenticationError, UnknownTransport, UnknownDatabase, \
    RemoteHostCommandError

ENV_FILE = os.path.join('config', 'env.json')
_config = None
_AVAILABLE_TRANSPORTS = frozenset({'SSH', 'MySQL'})
_connections = {transport: list() for transport in _AVAILABLE_TRANSPORTS}
""" Структура - что-то вроде
_connections = {
    'MySQL': [
        {'conn': `some_conn_instance`, 'env': `conn environment`},
        {'conn': `another_conn_instance`, 'env': `conn environment`}
    ],
    'SSH': [
        ...
        ...
    ]
}"""



class MySQLTransport:
    NAME = 'MySQL'

    def __init__(self, host, port, login, password):
        self.env = dict(
            host=host,
            port=port,
            user=login,
            password=password)
        self.conn = None
        self.is_connected = False
        self.persistent = False

    # Тут точно ничего не нужно?
    # А если объект по какой-то причине будет удалён вне менеджера
    # контекста, соединение же всё равно закрыть нужно?
    def __del__(self):
        pass

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def connect(self, database=None, persistent=False):
        self.env.update(dict(database=database))
        self.persistent = persistent
        if persistent and self.is_connected:
            self.conn = _get_connection(self)
            return
        try:
            self.conn = pymysql.connect(**self.env,
                                         charset='utf8',
                                         cursorclass=pymysql.cursors.DictCursor,
                                         unix_socket=False)
        # Вот тут не знаю, как ещё определить ошибку
        # Костыльно, но других по-другому не знаю
        except pymysql.err.OperationalError as e_info:
            if "Access denied" in str(e_info):
                raise AuthenticationError(self.env['user'], self.env['password'])
            elif "Can't connect to MySQL server" in str(e_info):
                raise TransportConnectionError(self.env['host'], self.env['port'])
        except pymysql.err.InternalError as e_info:
            if "Unknown database" in str(e_info):
                raise UnknownDatabase(database)
        if persistent:
            _connections[self.NAME].append(self)
        self.is_connected = True

    # Вот эта тема мне тоже не сишком нравится
    # Как можно более красиво хранить не открытую сессию?
    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except pymysql.err.Error:
                pass
            self.conn = None
        if self.is_connected and self.persistent:
            _connections[self.NAME].remove(self)
            self.is_connected = False

    def sqlexec(self, sql):
        with self.conn.cursor() as curr:
            try:
                curr.execute(sql)
            except Exception as e_info:
                raise MySQLError(e_info)
        self.conn.commit()
        return curr.fetchall()


class SSHTransport:
    NAME = 'SSH'

    def __init__(self, host, port, login, password):
        self.env = dict(
            hostname=host,
            port=port,
            username=login,
            password=password)
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.is_connected = False
        self.persistent = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def connect(self, persistent=False):
        self.persistent = persistent
        if persistent and self.is_connected:
            self.conn = _get_connection(self)
            return
        try:
            self.conn.connect(**self.env)
        except paramiko.ssh_exception.AuthenticationException:
            raise AuthenticationError(self.env['username'], self.env['password'])
        except Exception:
            raise TransportConnectionError(self.env['hostname'], self.env['port'])
        if persistent:
            _connections[self.NAME].append(self)
            self.is_connected = True

    def close(self):
        self.conn.close()
        if self.is_connected and self.persistent:
            _connections[self.NAME].remove(self)
        self.is_connected = False

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
        # Если наследовать новый Exception для этого - будет выглядеть
        # велосипедно. Может, тогда вообще не перехватывать этот?
        except FileNotFoundError:
            raise TransportError('File not found')
        return data


def close_all_connections():
    # будет тогда же, когда напишу закрытие одного)
    pass


# Выглядит костыльно, не знаю, как иначе
def _get_connection(transport):
    for connected in _connections[transport.NAME]:
        if connected.env == transport.env:
            return connected.conn


def get_transport(transport_name,
                  host=None,
                  port=None,
                  login=None,
                  password=None):
    if transport_name not in _AVAILABLE_TRANSPORTS:
        raise UnknownTransport(transport_name)

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


def get_config():
    global _config
    if not _config:
        with open(ENV_FILE) as f:
            _config = json.load(f)
    return _config
