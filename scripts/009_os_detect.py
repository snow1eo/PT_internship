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
        raw_os = ssh.execute_show('uname -a')
        if not raw_os.startswith('Linux'):
            return Status.COMPLIANT, raw_os.split()[0]
        raw_os = raw_os.lower()
        if 'debian' in raw_os:
            return Status.COMPLIANT, 'Debian Linux'
        elif 'centos' in raw_os:
            return Status.COMPLIANT, 'CentOS Linux'
        elif 'ubuntu' in raw_os:
            return Status.COMPLIANT, 'Ubuntu Linux'
        elif 'arch' in raw_os:
            return Status.COMPLIANT, 'Arch Linux'
        else:
            return Status.COMPLIANT, 'Unknown Linux'
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, ''.join(traceback.format_exception(*exc_info))
    return Status.COMPLIANT, None
