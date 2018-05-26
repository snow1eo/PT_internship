import sys
import traceback

from modules.errors import TransportConnectionError
from modules.functions import get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_compliance_env('303')
        sql = get_transport('MySQL')
        tables_privs = sql.load_table('mysql.tables_priv')
        if not env['whitelist']:
            return Status.COMPLIANT, "There's no whitelist"
        if not tables_privs:
            return Status.COMPLIANT, "Table has no privileges"
        wrong = list()
        for table in tables_privs:
            if env['database'] != table['Db'] or \
                    env['table'] != table['Table_name']:
                continue
            if table['User'] not in env['whitelist']:
                wrong.append(table['User'])
        if wrong:
            return Status.NOT_COMPLIANT, ", ".join(wrong)
        else:
            return Status.COMPLIANT, "Privileges match whitelist"
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]
