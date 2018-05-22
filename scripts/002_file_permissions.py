from modules.database import get_controls
from modules.errors import TransportConnectionError, RemoteHostCommandError
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['002']['env']
        ssh = get_transport('SSH')
        return ssh.check_permissions(**env)
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
