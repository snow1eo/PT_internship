import importlib
from time import sleep

import docker

from modules.statuses import Status
from modules.transports import get_transport, get_config
# Оставлю так, не нравятся мне _ в файлах
test0 = importlib.import_module('.000_test_file_exist', package='scripts')
test1 = importlib.import_module('.001_test_db_exist', package='scripts')

PATH = 'tests'
port_ssh = get_config()['transports']['SSH']['port']
port_sql = get_config()['transports']['MySQL']['port']
env_sql = get_config()['transports']['MySQL']['environment']
containers_env = {
    'Dockerfile_ubuntu_sshd': {
        'name': 'cont_ubuntu_sshd',
        'ports': {'22/tcp': port_ssh}
    },
    'Dockerfile_mariadb': {
        'name': 'mariadb',
        'ports': {'3306/tcp': ('127.0.0.1', port_sql)},
        'environment': env_sql
    }
}


def setup_module():    
    client = docker.from_env()
    client.containers.prune()
    for dockerfile, container_env in containers_env.items():
        images = client.images.build(path=PATH, dockerfile=dockerfile)
        try:
            client.containers.run(image=images[0],
                                  detach=True,
                                  **container_env)
        except Exception as e:
            if str(e).startswith('409 Client Error: Conflict'):
                pass
            else:
                print(e)
    client.containers.prune()
    sleep(15)  # waiting for start containers


def teardown_module():
    containers = docker.from_env().containers.list()
    running_containers = {env['name'] for env in containers_env.values()}
    for container in containers:
        if container.name in running_containers:
            container.stop()
            container.remove()


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
