import re
import sys
import traceback

from modules.errors import TransportConnectionError, SSHFileNotFound
from modules.functions import get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        ssh = get_transport('SSH',
                host="172.16.22.2",
                port=22,
                user="admin",
                password="P@ssw0rd")

        ssh.execute("terminal pager 0")
        config = ssh.execute_show("sh running-config logging")

        if log_mode == "logging on" or log_mode == "logging enable":
            return Status.COMPLIANT, None
        return Status.NOT_COMPLIANT, log_mode
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]
    return Status.COMPLIANT, None
