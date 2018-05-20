from modules.database import get_controls
from modules.errors import TransportConnectionError, RemoteHostCommandError
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['002']['env']
        ssh = get_transport('SSH')
        data = ssh.execute_show("ls -lad '{filename}'".format(**env))
        if not data:
            return Status.NOT_APPLICABLE, 'File not found'
        else:
            data = data.split()
            data[0] = oct(int(''.join(
                ['0' if p == '-' else '1' for p in data[0][1:]]), 2))[2:]
            if data[0] != env['permissions']:
                return Status.NOT_COMPLIANT, None
            try:
                if data[2] != env['owner']:
                    return Status.NOT_COMPLIANT, None
                elif data[3] != env['group']:
                    return Status.NOT_COMPLIANT, None
            except KeyError:
                pass
            return Status.COMPLIANT, None
    except (TransportConnectionError, RemoteHostCommandError):
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
