from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport
from modules.errors import TransportConnectionError, MySQLError


def main():
    env = get_controls()['001']['env']
    try:
        with get_transport('MySQL') as sql:
            try:
                databases = [db['Database'] for db in sql.sqlexec('SHOW DATABASES')]
                if env['db_name'] not in databases:
                    return Status.NOT_COMPLIANT
                tables = [
                    table['Tables_in_{db_name}'.format(**env)]
                    for table in sql.sqlexec('SHOW TABLES FROM {db_name}'.format(**env))
                ]
                if env['table_name'] not in tables:
                    return Status.NOT_COMPLIANT
                sql.connect(env['db_name'])
                if sql.sqlexec('''SELECT * FROM {table_name}'''.format(**env)):
                        return Status.COMPLIANT
                return Status.NOT_COMPLIANT
            except MySQLError:
                return Status.ERROR
    except TransportConnectionError:
        return Status.NOT_APPLICABLE
    except Exception:
        return Status.ERROR
