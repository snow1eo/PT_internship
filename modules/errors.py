# Database/Config (controls.json) Errors


class ConfigError(Exception):
    def __init__(self, cfg_name):
        self.cfg_name = cfg_name

    def __str__(self):
        return "{} doesn't match scripts".format(self.cfg_name)


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
    def __init__(self, request):
        self.request = request

    def __str__(self):
        return self.request


class RemoteHostCommandError(TransportError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class PermissionDenied(RemoteHostCommandError):
    pass


class SSHFileNotFound(TransportError):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return self.filename


class AuthenticationError(TransportConnectionError):
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def __str__(self):
        return 'user: {}, pass: {}'.format(self.user, self.password)


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


class SNMPError(TransportError):
    def __init__(self, indication):
        self.indication = indication

    def __str__(self):
        return "SNMP indicate error: {}".format(self.indication)


class SNMPStatusError(TransportError):
    def __init__(self, status, index):
        self.status = status
        self.index = index

    def __str__(self):
        return "SNMP status error: {} at {}".format(self.status, self.index)
