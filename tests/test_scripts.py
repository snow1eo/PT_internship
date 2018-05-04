import importlib
from time import sleep

import docker

from modules.statuses import Status
from modules.transports import get_transport

# Оставлю так, не нравятся мне _ в файлах
test0 = importlib.import_module('.000_test_file_exist', package='scripts')
test1 = importlib.import_module('.001_test_db_exist', package='scripts')


# Тут такая беда, mariadb не успевает от одного теста 
# оправиться и начинает следующий, где соединения падают
# Может, имеет смысл сделать несколько попыток подключения
# с таймаутом вместо этого костыля?
def teardown_module():
    sleep(3)


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


def test_000_file_exist_3():
    status = None   # just for situation when container didn't start
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd':
            container.stop()
            status = test0.main()
            container.start()
    assert status == Status.NOT_APPLICABLE


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


def test_001_database_exist_3():
    status = None   # just for situation when container didn't start
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'mariadb':
            container.stop()
            status = test1.main()
            container.start()
    assert status == Status.NOT_APPLICABLE
