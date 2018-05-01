import importlib
import os
import sys
from time import sleep

import docker

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.transports import get_transport, get_config
from modules.statuses import Statuses


PATH = 'tests'
DOCKER_FILE_UBUNTU = 'Dockerfile_ubuntu_sshd'
PORT_SSH = get_config()['transports']['SSH']['port']
DOCKER_FILE_MARIADB = 'Dockerfile_mariadb'
PORT_SQL = get_config()['transports']['MySQL']['port']
ENV_SQL = get_config()['transports']['MySQL']['environment']


def setup_module():
    client = docker.from_env()
    images = client.images.build(path=PATH, dockerfile=DOCKER_FILE_UBUNTU)
    try:
        cont = client.containers.run(image=images[0],
                                     detach=True,
                                     ports={'22/tcp': PORT_SSH},
                                     name='cont_ubuntu_sshd',
                                     auto_remove=False)
    except Exception as e:
        if str(e).startswith('409 Client Error: Conflict'):
            pass
        else:
            print(e)
    # Есть pull, но он работает неадекватно - медленно,
    # иногда падает и постоянно качает заново, кажется
    images = client.images.build(path=PATH, dockerfile=DOCKER_FILE_MARIADB)
    try:
        cont = client.containers.run(image=images[0],
                                     detach=True,
                                     ports={'3306/tcp': ('127.0.0.1', PORT_SQL)},         
                                     environment=ENV_SQL,
                                     name='mariadb',
                                     auto_remove=False)
    except Exception as e:
        if str(e).startswith('409 Client Error: Conflict'):
            pass
        else:
            print(e)
    sleep(5)


def teardown_module():
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd' or\
           container.name == 'mariadb':
            container.stop()
            container.remove()


def teardown_module():
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd':
            container.stop()
            container.remove()


def test_000_file_exist_1():
    ssh = get_transport('SSH')
    ssh.connect()
    ssh.execute('touch /testfile')
    mod = importlib.import_module('.000_test_file_exist', package='scripts')
    assert mod.main() == Statuses.COMPLIANT.value


def test_000_file_exist_2():
    ssh = get_transport('SSH')
    ssh.connect()
    try:
        ssh.execute('rm -f /testfile')
    except Exception as e_info:
        pass
    mod = importlib.import_module('.000_test_file_exist', package='scripts')
    assert mod.main() == Statuses.NOT_COMPLIANT.value


def test_000_file_exist_3():
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd':
            container.stop()
            mod = importlib.import_module('.000_test_file_exist', package='scripts')
            status = mod.main()
            container.start()
    assert status == Statuses.NOT_APPLICABLE.value


def test_000_file_exist_4():
    pass
    # TODO (HOW?)
