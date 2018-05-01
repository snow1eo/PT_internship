import os
import sys
from time import sleep

import docker
import pytest

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.transports import get_config, get_transport, SSHTransport, \
    TransportCreationError, AuthenticationError, TransportConnectionError, \
    TransportError

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
        client.containers.run(image=images[0],
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
        client.containers.run(image=images[0],
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


def test_get_transport_from_params_pass():
    ssh = get_transport('SSH', 'localhost', 22022, 'root', 'pwd')
    assert isinstance(ssh, SSHTransport)


def test_get_transport_from_config_pass():
    ssh = get_transport('SSH')
    assert isinstance(ssh, SSHTransport)


def test_get_transport_except():
    with pytest.raises(TransportCreationError) as e_info:
        get_transport('noway')
    assert str(e_info).endswith('UnknownTransport')


class TestSSHTransport:
    def test_connect_pass(self):
        with get_transport('SSH') as ssh:
            ssh.connect()

    def test_connect_wrong_auth(self):
        with get_transport('SSH', password='wrong') as ssh,\
                        pytest.raises(AuthenticationError) as e_info:
            ssh.connect()
        assert str(e_info).endswith('Authentication failed')

    def test_connect_wrong_host(self):
        with get_transport('SSH', port=666) as ssh,\
                        pytest.raises(TransportConnectionError) as e_info:
            ssh.connect()
        assert str(e_info).endswith("Couldn't connect to host")

    def test_execute_pass(self):
        with get_transport('SSH') as ssh:
            ssh.connect()
            assert isinstance(ssh.execute('ls /'), tuple)

    def test_execute_except(self):
        with get_transport('SSH', login='testuser', password='pass') as ssh,\
                        pytest.raises(TransportError) as e_info:
            ssh.connect()
            ssh.execute('wrong_command')

    def test_get_file_pass(self):
        with get_transport('SSH') as ssh:
            ssh.connect()
            assert isinstance(ssh.get_file('/etc/passwd'), bytes)

    def test_get_file_except(self):
        with get_transport('SSH') as ssh, pytest.raises(TransportError):
            ssh.connect()
            ssh.get_file('/wrong_file')
