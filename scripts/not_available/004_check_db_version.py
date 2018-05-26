import re
import sys
import traceback

from modules.errors import TransportConnectionError
from modules.functions import get_compliance_env, get_global_variables
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        relevant_ver = get_compliance_env('004')['relevant_version']
        sql = get_transport('MySQL')
        raw_version = get_global_variables(sql)['VERSION']
        if get_sql_version(raw_version) == relevant_ver:
            return Status.COMPLIANT, None
        else:
            return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]


def get_sql_version(raw_version):
    pattern = re.compile(r'\d+\.\d+\.\d+')
    version = re.findall(pattern, raw_version)
    return 'unknown' if not version else version[0]
