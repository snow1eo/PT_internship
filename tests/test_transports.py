import os
import sys
from time import sleep

import docker
import pytest

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.transports import get_transport, SshTransport, \
    TransportCreationError, AuthenticationError, TransportConnectionError, \
    TransportError


PATH = 'tests'
DOCKER_FILE = 'Dockerfile_ubuntu_sshd'
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
    while client.containers.list()[-1].status != 'running':  # костыльно немного,
        pass                                                 # но иначе не выходит
    sleep(5)
    client.containers.prune()


def teardown_module():
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd':
            container.stop()
            container.remove()


def test_get_transport_from_params_pass():
    ssh = get_transport('ssh', 'localhost', 22022, 'root', 'pwd')
    assert isinstance(ssh, SshTransport)


def test_get_transport_from_config_pass():
    ssh = get_transport('ssh')
    assert isinstance(ssh, SshTransport)


def test_get_transport_except():
    with pytest.raises(TransportCreationError) as e_info:
        get_transport('noway')
    assert str(e_info).endswith('UnknownTransport')


class TestSshTransport:
    def test_connect_pass(self):
        with get_transport('ssh') as ssh:
            ssh.connect()

    def test_connect_wrong_auth(self):
        with get_transport('ssh', password='wrong') as ssh,\
                        pytest.raises(AuthenticationError) as e_info:
            ssh.connect()
        assert str(e_info).endswith('Authentication failed')

    def test_connect_wrong_host(self):
        with get_transport('ssh', port=666) as ssh,\
                        pytest.raises(TransportConnectionError) as e_info:
            ssh.connect()
        assert str(e_info).endswith("Couldn't connect to host")

    def test_execute_pass(self):
        with get_transport('ssh') as ssh:
            ssh.connect()
            assert isinstance(ssh.execute('ls /'), tuple)

    def test_execute_except(self):
        with get_transport('ssh', login='testuser', password='pass') as ssh,\
                        pytest.raises(TransportError) as e_info:
            ssh.connect()
            ssh.execute('wrong_command')

    def test_get_file_pass(self):
        with get_transport('ssh') as ssh:
            ssh.connect()
            assert isinstance(ssh.get_file('/etc/passwd'), bytes)

    def test_get_file_except(self):
        with get_transport('ssh') as ssh, pytest.raises(TransportError):
            ssh.connect()
            ssh.get_file('/wrong_file')
