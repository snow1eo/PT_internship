from modules.database import get_controls
from modules.errors import TransportConnectionError, SSHFileNotFound
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['000']['env']
        ssh = get_transport('SSH')
        ssh.get_file(env['filename'])
    except SSHFileNotFound:
        return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
    return Status.COMPLIANT, None
