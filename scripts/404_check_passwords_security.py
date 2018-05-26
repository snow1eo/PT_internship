import re
import sys
import traceback

from netmiko import ConnectHandler

from modules.errors import TransportConnectionError, SSHFileNotFound
from modules.functions import get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        device = ConnectHandler(device_type='cisco_ios', ip='172.16.22.2', username='admin', password='P@ssw0rd')
        password_mode = device.send_command("sh running-config enable")
        if password_mode.endswith("encrypted\n"):
            return Status.COMPLIANT, None
        return Status.NOT_COMPLIANT, password_mode
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]
    return Status.COMPLIANT, None
