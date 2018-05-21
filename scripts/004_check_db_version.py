from modules.database import get_controls
from modules.errors import TransportConnectionError
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        relevant_ver = get_controls()['004']['env']['relevant_version']
        sql = get_transport('MySQL')
        if sql.get_version() == relevant_ver:
            return Status.COMPLIANT, None
        else:
            return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
