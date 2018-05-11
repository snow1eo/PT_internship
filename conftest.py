import os
from shutil import rmtree, copytree
from time import sleep

import docker
import pytest

from modules.database import reset_database
from modules.transports import get_transport_config, close_all_connections

DOCKER_PATH = os.path.join('tests', 'containers')
TEST_DIR = '.test_tmp'
port_ssh = get_transport_config('SSH').port
port_sql = get_transport_config('MySQL').port
env_sql = get_transport_config('MySQL').environment
port_snmp = get_transport_config('SNMP').port
env_snmp = get_transport_config('SNMP').environment
PORT_DEB_SSH = 23022
containers_env = {
    'ubuntu_sshd': {
        'name': 'cont_ubuntu_sshd',
        'ports': {'22/tcp': port_ssh}
    },
    'mariadb': {
        'name': 'mariadb',
        'ports': {'3306/tcp': ('127.0.0.1', port_sql)},
        'environment': env_sql
    },
    'debian-snmp': {
        'name': 'debian-snmp',
        'ports': {'161/udp': port_snmp,
                  '22/tcp': PORT_DEB_SSH}
    }
}


def pytest_sessionstart(session):
    client = docker.from_env()
    for container_name, container_env in containers_env.items():
        images = client.images.build(
            path=os.path.join(DOCKER_PATH, container_name),
            dockerfile='Dockerfile')
        try:
            client.containers.run(image=images[0],
                                  detach=True,
                                  auto_remove=True,
                                  **container_env)
        except Exception as e:
            if str(e).startswith('409 Client Error: Conflict'):
                pass
            else:
                print(e)
    client.containers.prune()
    sleep(15)  # waiting for start containers


def pytest_sessionfinish(session, exitstatus):
    close_all_connections()
    containers = docker.from_env().containers.list()
    running_containers = {env['name'] for env in containers_env.values()}
    for container in containers:
        if container.name in running_containers:
            container.stop()


@pytest.fixture()
def no_ssh_connections(monkeypatch):
    close_all_connections()
    monkeypatch.delattr('paramiko.SSHClient.connect')


@pytest.fixture()
def no_mysql_connections(monkeypatch):
    close_all_connections()
    monkeypatch.delattr('pymysql.connect')


@pytest.fixture()
def no_transports(monkeypatch):
    close_all_connections()
    monkeypatch.delattr('modules.transports._TRANSPORTS')


@pytest.fixture(scope='module')
def change_dir(request):
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
