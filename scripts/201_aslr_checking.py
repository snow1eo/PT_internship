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
        env = get_compliance_env('013')
        ssh = get_transport('SSH')
        param = ssh.execute_show('/sbin/sysctl kernel.randomize_va_space').split()[-1]
        if param == '2':
            return Status.COMPLIANT, None
        else:
            return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]
