from modules.functions import get_compliance_env, get_sql_version
from modules.errors import TransportConnectionError
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        relevant_ver = get_compliance_env('004')['relevant_version']
        sql = get_transport('MySQL')
        if get_sql_version(sql) == relevant_ver:
            return Status.COMPLIANT, None
        else:
            return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
