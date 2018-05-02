#!/usr/bin/env python3

from modules.statuses import Statuses
from modules.transports import get_transport, UnknownDatabase, \
        TransportConnectionError


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
            if 'testdb' not in databases:
                return Statuses.NOT_COMPLIANT.value
            tables = sql.sqlexec('SHOW TABLES FROM testdb')
            if not tables:
                return Statuses.NOT_COMPLIANT.value
            for table in tables:
                if sql.sqlexec('''SHOW COLUMNS FROM {} FROM
                               testdb'''.format(table['Tables_in_testdb'])):
                    return Statuses.COMPLIANT.value
            return Statuses.NOT_COMPLIANT.value
        except MySQLError as err:
            return Statuses.ERROR.value
