#!/usr/bin/env python3

from modules.statuses import Statuses
from modules.transports import get_transport, TransportConnectionError, TransportError


def main():
    try:
        ssh = get_transport('SSH')
        ssh.connect()
    except TransportConnectionError as e_info:
        if str(e_info).endswith("Couldn't connect to host"):
            return Statuses.NOT_APPLICABLE.value
        else:
            return Statuses.ERROR.value
    try:
        ssh.get_file('/testfile')
    except TransportError as err:
        if str(err).endswith('File not found'):
            return Statuses.NOT_COMPLIANT.value
        else:
            return Statuses.ERROR.value
    return Statuses.COMPLIANT.value
