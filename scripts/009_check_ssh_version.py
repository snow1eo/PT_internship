import sys
import traceback

from modules.errors import TransportConnectionError, SSHFileNotFound
from modules.functions import get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport


def main():
    ssh = get_transport('SSH')
    config = ssh.execute_show("sh running-config")
    


