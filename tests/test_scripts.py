import importlib

import docker

from modules.statuses import Status
from modules.transports import get_transport
import scripts  # for Windows

test0 = importlib.import_module('.000_test_file_exist', package='scripts')
test1 = importlib.import_module('.001_test_db_exist', package='scripts')


def test_000_file_exist_1():
    with get_transport('SSH') as ssh:
        ssh.execute('touch /testfile')
    assert test0.main() == Status.COMPLIANT


def test_000_file_exist_2():
    with get_transport('SSH') as ssh:
        try:
            ssh.execute('rm -f /testfile')
        except Exception:
            pass
    assert test0.main() == Status.NOT_COMPLIANT


def test_000_file_exist_3(no_ssh_connections):
    assert test0.main() == Status.NOT_APPLICABLE


def test_001_database_exist_1():
    with get_transport('MySQL') as sql:
        sql.sqlexec('CREATE DATABASE IF NOT EXISTS test_db')
        sql.close()
        sql.connect('test_db')
        sql.sqlexec("""CREATE TABLE IF NOT EXISTS test_table (
                    name VARCHAR(20), owner VARCHAR(20))""")
        sql.sqlexec("INSERT INTO test_table VALUES ('Dolly', 'Me')")
    assert test1.main() == Status.COMPLIANT


def test_001_database_exist_2():
    with get_transport('MySQL') as sql:
        sql.sqlexec('DROP DATABASE IF EXISTS test_db')
    assert test1.main() == Status.NOT_COMPLIANT


def test_001_database_exist_3(no_mysql_connections):
    assert test1.main() == Status.NOT_APPLICABLE
