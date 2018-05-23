import sys
import traceback

from modules.errors import TransportConnectionError, SSHFileNotFound
from modules.functions import get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_compliance_env('000')
        ssh = get_transport('SSH')
        ssh.get_file(env['filename'])
    except SSHFileNotFound:
        return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, ''.join(traceback.format_exception(*exc_info))
    return Status.COMPLIANT, None
