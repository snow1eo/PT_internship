import importlib

from modules.database import get_controls
from modules.statuses import Status
from modules.transports import get_transport, close_all_connections

test0 = importlib.import_module('.000_test_file_exist', package='scripts')
test1 = importlib.import_module('.001_test_db_exist', package='scripts')
test2 = importlib.import_module('.002_file_permissions', package='scripts')
test3 = importlib.import_module('.003_check_dump_for_pass', package='scripts')


def test_000_file_exist_1(run_docker):
    env = get_controls()['000']['env']
    ssh = get_transport('SSH')
    ssh.execute('touch "{filename}"'.format(**env))
    assert test0.main()[0] == Status.COMPLIANT


def test_000_file_exist_2(run_docker):
    env = get_controls()['000']['env']
    ssh = get_transport('SSH')
    try:
        ssh.execute('rm -f "{filename}"'.format(**env))
    except Exception:
        pass
    assert test0.main()[0] == Status.NOT_COMPLIANT


def test_000_file_exist_3(run_docker, no_ssh_connections):
    close_all_connections()
    assert test0.main()[0] == Status.NOT_APPLICABLE


def test_000_file_exist_4(run_docker, no_transports):
    close_all_connections()
    assert test0.main()[0] == Status.ERROR and test1.main()[1]


def test_001_database_exist_1(run_docker):
    env = get_controls()['001']['env']
    sql = get_transport('MySQL')
    sql.sqlexec('CREATE DATABASE IF NOT EXISTS {db_name}'.format(**env))
    sql.connect(database=env['db_name'])
    sql.sqlexec("""CREATE TABLE IF NOT EXISTS {table_name} (
                name VARCHAR(20), owner VARCHAR(20))""".format(**env))
    sql.sqlexec("INSERT INTO {table_name} VALUES ('Dolly', 'Me')".format(**env))
    assert test1.main()[0] == Status.COMPLIANT


def test_001_database_exist_2(run_docker):
    env = get_controls()['001']['env']
    sql = get_transport('MySQL')
    sql.sqlexec('DROP DATABASE IF EXISTS {db_name}'.format(**env))
    assert test1.main()[0] == Status.NOT_COMPLIANT


def test_001_database_exist_3(run_docker, no_mysql_connections):
    assert test1.main()[0] == Status.NOT_APPLICABLE


def test_001_database_exist_4(run_docker, no_transports):
    assert test1.main()[0] == Status.ERROR and test1.main()[1]


def test_002_permissions_1(run_docker):
    env = get_controls()['002']['env']
    ssh = get_transport('SSH')
    # transform string-permissions to oct
    oct_permissions = oct(int(''.join(
        ['0' if p == '-' else '1' for p in env['permissions'][1:]]), 2))[2:]
    ssh.execute('chmod {} "{}"'.format(oct_permissions, env['filename']))
    assert test2.main()[0] == Status.COMPLIANT


def test_002_permissions_2(run_docker):
    env = get_controls()['002']['env']
    ssh = get_transport('SSH')
    # transform string-permissions to oct and changing last bit using XOR
    oct_permissions = oct(int(''.join(
        ['0' if p == '-' else '1' for p in env['permissions'][1:]]), 2) ^ 1)[2:]
    ssh.execute('chmod {} "{}"'.format(oct_permissions, env['filename']))
    assert test2.main()[0] == Status.NOT_COMPLIANT


def test_002_permissions_3(run_docker, no_ssh_connections):
    close_all_connections()
    assert test2.main()[0] == Status.NOT_APPLICABLE


def test_002_permissions_4(run_docker, no_transports):
    close_all_connections()
    assert test2.main()[0] == Status.ERROR and test1.main()[1]


def test_003_mem_dump_1(run_docker, no_ssh_execute):
    assert test3.main()[0] == Status.COMPLIANT


def test_003_mem_dump_2(run_docker):
    assert test3.main()[0] == Status.NOT_COMPLIANT


def test_003_mem_dump_3(run_docker, no_ssh_connections):
    assert test3.main()[0] == Status.NOT_APPLICABLE


def test_003_mem_dump_4(run_docker, no_transports):
    assert test1.main()[0] == Status.ERROR and test1.main()[1]
