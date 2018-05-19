from modules.database import get_controls
from modules.errors import TransportConnectionError, RemoteHostCommandError
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['002']['env']
        ssh = get_transport('SSH')
        data = ssh.execute_show("ls -la '{filename}'".format(**env))
        if not data:
            return Status.NOT_APPLICABLE, 'File not found'
        else:
            curr_permissions = data.split()[0]
            if curr_permissions == env['permissions']:
                return Status.COMPLIANT, None
            else:
                return Status.NOT_COMPLIANT, None
    except (TransportConnectionError, RemoteHostCommandError):
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
