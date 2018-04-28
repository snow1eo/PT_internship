#!/usr/bin/env python3

from modules.transports import get_transport, TransportConnectionError, TransportError
from modules.statuses import STATUS_COMPLIANT, STATUS_NOT_COMPLIANT,\
                             STATUS_NOT_APPLICABLE, STATUS_ERROR
def main():
    try:
        ssh = get_transport('ssh')
        ssh.connect()
    except TransportConnectionError as e_info:
        if str(e_info).endswith("Couldn't connect to host"):
            return STATUS_NOT_APPLICABLE
        else:
            return STATUS_ERROR
    try:
        data = ssh.get_file('/testfile')
    except TransportError as err:
        if str(err).endswith('File not found'):
            return STATUS_NOT_COMPLIANT
        else:
            return STATUS_ERROR
    return STATUS_COMPLIANT
