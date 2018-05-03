#!/usr/bin/env python3

import os

from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport, TransportConnectionError, TransportError


def main():
    env = get_controls()['000']['env']
    try:
        with get_transport('SSH') as ssh:
            try:
                ssh.get_file(os.path.join(env['path'], env['name']))
            except TransportError as err:
                if str(err).endswith('File not found'):
                    return Status.NOT_COMPLIANT
                else:
                    return Status.ERROR
            return Status.COMPLIANT
    except TransportConnectionError:
        return Status.NOT_APPLICABLE
    except Exception:
        return Status.ERROR
