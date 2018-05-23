from shlex import quote

from modules.functions import get_compliance_env
from modules.errors import TransportConnectionError, RemoteHostCommandError, \
    PermissionDenied
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_compliance_env('002')
        ssh = get_transport('SSH')
        if check_permissions(env, get_permissions(ssh, env['filename'])):
            return Status.COMPLIANT, make_message_compl(env)
        else:
            return Status.NOT_COMPLIANT, make_message_not_compl(
                env, get_permissions(ssh, env['filename']))
    except PermissionDenied:
        return Status.NOT_APPLICABLE, 'No access to file'
    except RemoteHostCommandError:
        return Status.COMPLIANT, 'File not found'
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)


def check_permissions(required, current):
    required = required.copy()
    if ~int(required.pop('permissions'), 8) & int(current.pop('permissions'), 8):
        return False
    required.pop('filename')
    required.setdefault('owner', current['owner'])
    required.setdefault('group', current['group'])
    return required == current


def get_permissions(ssh, filename):
    data = ssh.execute_show(
            'stat --printf="%a %U %G" {}'.format(quote(filename))).split()
    return dict(
        permissions=data[0],
        owner=data[1],
        group=data[2])


def make_message_compl(curr):
    msg = "{filename}:{permissions}"
    if 'owner' in curr:
        msg += '::{owner}'
    if 'group' in curr:
        msg += ':{group}'
    return msg.format(**curr)


def make_message_not_compl(req, curr):
    msg = "{filename}:{permissions}::{owner}:{group} != \
        {c_permission}::{c_owner}:{c_group}"
    return msg.format(**req,
        c_permission=curr['permissions'],
        c_owner=curr['owner'],
        c_group=curr['group'])
