from modules.database import get_controls
from modules.errors import TransportConnectionError
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        env = get_controls()['001']['env']
        sql = get_transport('MySQL')
        databases = [db['Database'] for db in sql.sqlexec('SHOW DATABASES')]
        if env['db_name'] not in databases:
            return Status.NOT_COMPLIANT, None
        tables = [
            table['Tables_in_{db_name}'.format(**env)]
            for table in sql.sqlexec('SHOW TABLES FROM {db_name}'.format(**env))
        ]
        if env['table_name'] not in tables:
            return Status.NOT_COMPLIANT, None
        sql.connect(env['db_name'])
        if sql.sqlexec('SELECT * FROM {table_name}'.format(**env)):
            return Status.COMPLIANT, None
        return Status.NOT_COMPLIANT, None
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
