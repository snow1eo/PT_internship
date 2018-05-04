# Database/Config (controls.json) Errors


class ConfigError(Exception):
    def __init__(self, cfg_name):
        self.cfg_name = cfg_name

    def __str__(self):
        return "{} doesn't match scripts".format(cfg_name)


# Transport Errors


class TransportError(Exception):
    pass


class TransportConnectionError(TransportError):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __str__(self):
        return "Couldn't connect to host {}:{}".format(self.host, self.port)


class TransportCreationError(TransportError):
    pass


class MySQLError(TransportError):
    pass


class RemoteHostCommandError(TransportError):
    pass


class AuthenticationError(TransportConnectionError):
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __str__(self):
        return 'login: {}, pass: {}'.format(self.login, self.password)


class UnknownTransport(TransportCreationError):
    def __init__(self, transport_name):
        self.transport_name = transport_name

    def __str__(self):
        return self.transport_name


class UnknownDatabase(TransportConnectionError):
    def __init__(self, db_name):
        self.db_name = db_name

    def __str__(self):
        return self.db_name
