from shlex import quote

from modules.database import get_controls
from modules.errors import TransportConnectionError, RemoteHostCommandError, \
    PermissionDenied
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['002']['env']
        ssh = get_transport('SSH')
        return check_permissions(ssh, **env)
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)


def check_permissions(ssh, filename, permissions, owner=None, group=None):
    try:
        data = ssh.execute_show(
            'stat --printf="%a %U %G" {}'.format(quote(filename)))
    except PermissionDenied:
        return Status.NOT_APPLICABLE, 'No access to file'
    except RemoteHostCommandError:
        return Status.COMPLIANT, 'File not found'
    permissions_, owner_, group_ = data.split()
    if sum((int(r) ^ 1) * int(c) for r, c in zip(
            format(int(permissions, 8), '0=12b'),
            format(int(permissions_, 8), '0=12b'))):
        return Status.NOT_COMPLIANT, "{}:{} != {}".format(
            filename, permissions, data[0])
    owner = owner or owner_
    group = group or group_
    if (owner_, group_) != (owner, group):
        return Status.NOT_COMPLIANT, "{}:{}::{}:{} != {}::{}:{}".format(
            filename, permissions, owner, group,
            permissions_, owner_, group_)
    else:
        return Status.COMPLIANT, "{}:{}::{}:{}".format(
            filename, permissions_, owner_, group_)