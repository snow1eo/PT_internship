#!/usr/bin/env python3

from modules.statuses import Statuses
from modules.transports import get_transport, UnknownDatabase, \
        TransportConnectionError
from modules.database import get_controls


ENV = get_controls()[-1]


def main():
    with get_transport('MySQL') as sql:
        try:
            sql.connect()
        except TransportConnectionError:
            return Statuses.NOT_APPLICABLE.value
        except Exception:
            return Statuses.ERROR.value
        try:
            databases = [db['Database'] for db in sql.sqlexec('SHOW DATABASES')]
            if ENV['db_name'] not in databases:
                return Statuses.NOT_COMPLIANT.value
            tables = [table['Tables_in_{db_name}'.format(**ENV)] for table in 
                      sql.sqlexec('SHOW TABLES FROM {}'.format(**ENV))]
            if ENV['table_name'] not in tables:
                return Statuses.NOT_COMPLIANT.value
            if sql.sqlexec('''SHOW COLUMNS FROM {table_name} FROM
                               {db_name}'''.format(**ENV)):
                    return Statuses.COMPLIANT.value
            return Statuses.NOT_COMPLIANT.value
        except MySQLError as err:
            return Statuses.ERROR.value
