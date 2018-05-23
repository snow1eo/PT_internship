from modules.functions import get_compliance_env
from modules.errors import TransportConnectionError, SSHFileNotFound
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_compliance_env('000')
        ssh = get_transport('SSH')
        ssh.get_file(env['filename'])
    except SSHFileNotFound:
        return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception as e_info:
        return Status.ERROR, repr(e_info)
    return Status.COMPLIANT, None
