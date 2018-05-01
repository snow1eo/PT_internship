import importlib
import os
import sys
from time import sleep

import docker

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.transports import get_transport
from modules.statuses import Statuses


PATH = r'tests'
DOCKER_FILE = r'./Dockerfile_ubuntu_sshd'
PORT = 22022


def setup_module():
    client = docker.from_env()
    images = client.images.build(path=PATH, dockerfile=DOCKER_FILE)
    try:
        cont = client.containers.run(image=images[0],
                                     detach=True,
                                     ports={'22/tcp': PORT},
                                     name='cont_ubuntu_sshd')
    except Exception as e:
        print(e)
    sleep(5)
    client.containers.prune()


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
