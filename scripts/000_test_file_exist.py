#!/usr/bin/env python3

import os

from modules.statuses import Statuses
from modules.transports import get_transport, TransportConnectionError, TransportError
from modules.database import get_controls


ENV = get_controls()['000']['env']


def main():
    with get_transport('SSH') as ssh:
        try:
            ssh.connect()
        except TransportConnectionError as e_info:
            if str(e_info).endswith("Couldn't connect to host"):
                return Statuses.NOT_APPLICABLE.value
            else:
                return Statuses.ERROR.value
        try:
            ssh.get_file(os.path.join(ENV['path'], ENV['name']))
        except TransportError as err:
            if str(err).endswith('File not found'):
                return Statuses.NOT_COMPLIANT.value
            else:
                return Statuses.ERROR.value
        return Statuses.COMPLIANT.value
