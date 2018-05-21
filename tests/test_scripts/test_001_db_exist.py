import importlib

from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport

test = importlib.import_module('.001_test_db_exist', package='scripts')


def test_compliant(run_docker):
    env = get_controls()['001']['env']
    sql = get_transport('MySQL')
    sql.sqlexec('CREATE DATABASE IF NOT EXISTS {db_name}'.format(**env))
    sql.connect(database=env['db_name'])
    sql.sqlexec("""CREATE TABLE IF NOT EXISTS {table_name} (
                name VARCHAR(20), owner VARCHAR(20))""".format(**env))
    sql.sqlexec("INSERT INTO {table_name} VALUES ('Dolly', 'Me')".format(**env))
    assert test.main()[0] == Status.COMPLIANT


def test_not_compliant(run_docker):
    env = get_controls()['001']['env']
    sql = get_transport('MySQL')
    sql.sqlexec('DROP DATABASE IF EXISTS {db_name}'.format(**env))
    assert test.main()[0] == Status.NOT_COMPLIANT


def test_not_applicable(run_docker, no_mysql_connections):
    assert test.main()[0] == Status.NOT_APPLICABLE


def test_error(run_docker, no_transports):
    assert test.main()[0] == Status.ERROR and test.main()[1]
