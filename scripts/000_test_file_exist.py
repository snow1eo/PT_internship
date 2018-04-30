#!/usr/bin/env python3

import json

from modules.transports import get_transport, TransportConnectionError, TransportError

with open('statuses.json') as f:
    statuses = json.load(f)


def main():
    try:
        ssh = get_transport('ssh')
        ssh.connect()
    except TransportConnectionError as e_info:
        if str(e_info).endswith("Couldn't connect to host"):
            return statuses['NOT_APPLICABLE']['code']
        else:
            return statuses['ERROR']['code']
    try:
        ssh.get_file('/testfile')
    except TransportError as err:
        if str(err).endswith('File not found'):
            return statuses['NOT_COMPLIANT']['code']
        else:
            return statuses['ERROR']['code']
    return statuses['COMPLIANT']['code']
