import os

from modules.database import get_controls
from modules.errors import TransportConnectionError, SSHFileNotFound
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['000']['env']
        ssh = get_transport('SSH')
        ssh.connect(persistent=True)
        ssh.get_file(os.path.join(env['path'], env['name']))
    except SSHFileNotFound:
        return Status.NOT_COMPLIANT
    except TransportConnectionError:
        return Status.NOT_APPLICABLE
    except Exception:
        return Status.ERROR
    return Status.COMPLIANT
