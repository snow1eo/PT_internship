import sys
import traceback
from shlex import quote
import re

from modules.errors import TransportConnectionError, RemoteHostCommandError, \
    PermissionDenied
from modules.functions import get_compliance_env, check_permissions, \
    get_permissions, make_message_compl, make_message_not_compl
from modules.statuses import Status
from modules.transports import get_transport
from modules.audit import get_packages


def main():
    try:
        ssh = get_transport('SSH')
        version = get_packages(ssh)['openssl'].split('-')[0]
        if '1.0.1' <=  version and version < '1.0.1f':
            return Status.NOT_COMPLIANT, None
        else:
            return Status.COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No SSH connection'
    except KeyError:
        return Status.NOT_APPLICABLE, 'No OpenSSL found'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]
