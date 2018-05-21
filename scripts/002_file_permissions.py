from shlex import quote

from modules.database import get_controls
from modules.errors import TransportConnectionError, RemoteHostCommandError
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['002']['env']
        env['filename'] = quote(env['filename'])
        ssh = get_transport('SSH')
        data = ssh.execute_show('stat --printf="%a %U %G" {filename}'.format(**env))
        if not data:
            return Status.NOT_APPLICABLE, 'File not found'
        else:
            data = data.split()
            if data[0] != env['permissions']:
                return Status.NOT_COMPLIANT, None
            try:
                if data[1] != env['owner']:
                    return Status.NOT_COMPLIANT, None
                elif data[2] != env['group']:
                    return Status.NOT_COMPLIANT, None
            except KeyError:
                pass
            return Status.COMPLIANT, None
    except (TransportConnectionError, RemoteHostCommandError):
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
