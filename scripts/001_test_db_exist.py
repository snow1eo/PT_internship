import sys
import traceback

from modules.errors import TransportConnectionError
from modules.functions import get_compliance_env
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_compliance_env('001')
        sql = get_transport('MySQL')
        databases = [db['Database'] for db in sql.sqlexec('SHOW DATABASES')]
        if env['db_name'] not in databases:
            return Status.NOT_COMPLIANT, "Database doesn't exist"
        tables = [
            table['Tables_in_{db_name}'.format(**env)]
            for table in sql.sqlexec('SHOW TABLES FROM {db_name}'.format(**env))
        ]
        if env['table_name'] not in tables:
            return Status.NOT_COMPLIANT, "Table doesn't exist"
        sql.connect(env['db_name'])
        if sql.sqlexec('SELECT * FROM {table_name}'.format(**env)):
            return Status.COMPLIANT, None
        return Status.NOT_COMPLIANT, "Table is empty"
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, ''.join(traceback.format_exception(*exc_info))
