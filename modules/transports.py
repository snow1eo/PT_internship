import paramiko
import json

class TransportError(Exception):
    pass

class TransportConnectionError(TransportError):
    pass

_config = None

class SSH_transport:
    def __init__(self, host, port, login, password):
        self.host     = host
        self.port     = port
        self.login    = login
        self.password = password
        self._conn    = paramiko.SSHClient()
        self._conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def connect(self):
        try:
            self._conn.connect(hostname = self.host,
                               port     = self.port,
                               username = self.login,
                               password = self.password)
        except paramiko.ssh_exception.AuthenticationException:
            raise TransportConnectionError('Authentication failed')
        except Exception:
            raise TransportConnectionError("Couldn't connect to host")

    def close(self):
        self._conn.close()

    def execute(self, command):
        stdin, stdout, stderr = self._conn.exec_command(command)
        err = stderr.read()
        if err:
            raise TransportError(err)
        return (stdin, stdout, stderr)

    def get_file(self, path):
        sftp = self._conn.open_sftp()
        try:
            with sftp.open(path) as f:
                data = f.read()
        except FileNotFoundError:
            raise TransportError('File not found')
        return data

_available_transports = {'ssh'}

def get_transport(transport_name,
                  host     = None,
                  port     = None,
                  login    = None,
                  password = None):
    if transport_name not in _available_transports:
        raise TransportError('UnknownTransport')

    if host is None or port is None or\
       login is None or password is None:
        conf = _get_config()
        if host is None:
            host = conf['host']
        if port is None:
            port = conf['transports'][transport_name]['port']
        if login is None:
            login = conf['transports'][transport_name]['login']
        if password is None:
            password = conf['transports'][transport_name]['password']

    if transport_name == 'ssh':
        return SSH_transport(host, port, login, password)
    else:
        raise TransportError('UnknownTransport')

def _get_config():
    global _config
    if not _config:
        with open('config.json') as f:
            _config = json.load(f)
    return _config