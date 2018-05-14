import importlib

from modules.statuses import Status
from modules.transports import get_transport, close_all_connections

test0 = importlib.import_module('.000_test_file_exist', package='scripts')
test1 = importlib.import_module('.001_test_db_exist', package='scripts')


def test_000_file_exist_1(build_docker):
    ssh = get_transport('SSH')
    ssh.execute('touch /testfile')
    assert test0.main()[0] == Status.COMPLIANT


def test_000_file_exist_2(build_docker):
    ssh = get_transport('SSH')
    try:
        ssh.execute('rm -f /testfile')
    except Exception:
        pass
    assert test0.main()[0] == Status.NOT_COMPLIANT


def test_000_file_exist_3(build_docker, no_ssh_connections):
    close_all_connections()
    assert test0.main()[0] == Status.NOT_APPLICABLE


def test_000_file_exist_4(build_docker, no_transports):
    close_all_connections()
    assert test0.main()[0] == Status.ERROR and test1.main()[1]


def test_001_database_exist_1(build_docker):
    sql = get_transport('MySQL')
    sql.sqlexec('CREATE DATABASE IF NOT EXISTS test_db')
    sql.connect(database='test_db')
    sql.sqlexec("""CREATE TABLE IF NOT EXISTS test_table (
                name VARCHAR(20), owner VARCHAR(20))""")
    sql.sqlexec("INSERT INTO test_table VALUES ('Dolly', 'Me')")
    assert test1.main()[0] == Status.COMPLIANT


def test_001_database_exist_2(build_docker):
    sql = get_transport('MySQL')
    sql.sqlexec('DROP DATABASE IF EXISTS test_db')
    assert test1.main()[0] == Status.NOT_COMPLIANT


def test_001_database_exist_3(build_docker, no_mysql_connections):
    assert test1.main()[0] == Status.NOT_APPLICABLE


def test_001_database_exist_4(build_docker, no_transports):
    assert test1.main()[0] == Status.ERROR and test1.main()[1]
