#!/usr/bin/env python3

from modules.transports import *

def main():
    try:
        ssh = get_transport('ssh')
        ssh.connect()
    except TransportConnectionError as e_info:
        if str(e_info).endswith("Couldn't connect to host"):
            return 3
        else:
            return 4
    try:
        data = ssh.get_file('/testfile')
    except TransportError as err:
        if str(err).endswith('File not found'):
            return 2
        else:
            return 4
    return 1