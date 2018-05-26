import sys
import traceback
from shlex import quote

from modules.errors import TransportConnectionError, RemoteHostCommandError, \
    PermissionDenied
from modules.functions import get_compliance_env, check_permissions, \
    get_permissions, make_message_compl, make_message_not_compl
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
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]
