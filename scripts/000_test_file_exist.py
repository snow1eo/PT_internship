import os

from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport
from modules.errors import TransportConnectionError, SSHFileNotFound


def main():
    env = get_controls()['000']['env']
    try:
        with get_transport('SSH') as ssh:
            try:
                ssh.get_file(os.path.join(env['path'], env['name']))
            except SSHFileNotFound:
                return Status.NOT_COMPLIANT
            return Status.COMPLIANT
    except TransportConnectionError:
        return Status.NOT_APPLICABLE
    except Exception:
        return Status.ERROR
