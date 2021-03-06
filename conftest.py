import os
from shutil import rmtree, copytree
from time import sleep

import docker
import pytest

from modules.database import reset_database
from modules.errors import TransportConnectionError
from modules.transports import get_transport_config, close_all_connections


@pytest.fixture(scope='session')
def run_docker(request):
    docker_path = os.path.join('tests', 'containers')
    port_ssh = get_transport_config('SSH').port
    port_sql = get_transport_config('MySQL').port
    env_sql = get_transport_config('MySQL').environment
    port_snmp = get_transport_config('SNMP').port
    containers_env = {
        'mariadb': {
            'name': 'mariadb',
            'ports': {'3306/tcp': ('127.0.0.1', port_sql)},
            'environment': env_sql
        },
        'debian-snmp': {
            'name': 'debian-snmp',
            'ports': {'161/udp': port_snmp,
                      '22/tcp': port_ssh}
        }
    }

    client = docker.from_env()
    started_containers = list()
    for container_name, container_env in containers_env.items():
        images = client.images.build(
            path=os.path.join(docker_path, container_name),
            dockerfile='./Dockerfile')
        try:
            client.containers.run(image=images[0],
                                  detach=True,
                                  auto_remove=True,
                                  **container_env)
            started_containers.append(container_name)
        except Exception as e:
            if str(e).startswith('409 Client Error: Conflict'):
                pass
            else:
                print(e)
    client.containers.prune()
    if started_containers:
        sleep(15)  # waiting for start containers

    def stop_container():
        close_all_connections()
        containers = docker.from_env().containers.list()
        for container in containers:
            if container.name in started_containers:
                container.stop()

    request.addfinalizer(stop_container)


def pytest_sessionfinish(session, exitstatus):
    close_all_connections()


@pytest.fixture()
def no_ssh_connections(monkeypatch):
    close_all_connections()
    monkeypatch.delattr('paramiko.SSHClient.connect')


@pytest.fixture()
def no_mysql_connections(monkeypatch):
    close_all_connections()
    monkeypatch.delattr('pymysql.connect')


@pytest.fixture()
def no_snmp_connections(monkeypatch):
    close_all_connections()

    def no_snmp(self):
        raise TransportConnectionError(None, None)
    
    monkeypatch.setattr('modules.transports.SNMPTransport.connect', no_snmp)


@pytest.fixture()
def no_transports(monkeypatch):
    close_all_connections()
    monkeypatch.delattr('modules.transports._TRANSPORTS')


@pytest.fixture()
def no_ssh_execute(monkeypatch):
    monkeypatch.setattr('modules.transports.SSHTransport.execute_show',
                        lambda self, x: None)
    monkeypatch.setattr('modules.transports.SSHTransport.execute',
                        lambda self, x: (None, None, None))


@pytest.fixture(scope='module')
def change_dir(request):
    TEST_DIR = '.test_tmp'
    if os.path.exists(TEST_DIR):
        rmtree(TEST_DIR)
    copytree('.', TEST_DIR)
    os.chdir(TEST_DIR)

    def clean():
        os.chdir('..')
        if os.path.exists(TEST_DIR):
            rmtree(TEST_DIR)

    request.addfinalizer(clean)


@pytest.fixture()
def create_new_database():
    reset_database()
