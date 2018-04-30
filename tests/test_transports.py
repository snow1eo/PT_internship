import pytest
import sys
import os
if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())

import docker
from time import sleep
from modules.transports import get_transport, SSH_transport,\
     TransportCreationError, AuthenticationError, TransportConnectionError,\
     TransportError

def setup_module(module):

    path = r'./tests/'
    dockerfile = r'./Dockerfile_ubuntu_sshd'

    client = docker.from_env()
    images = client.images.build(path = path, dockerfile = dockerfile)
    try:
        cont = client.containers.run(image  = images[0],
                                     detach = True,
                                     ports  = {'22/tcp' : 22022},
                                     name   = 'cont_ubuntu_sshd')
    except Exception as e:
        print(e)
    while client.containers.list()[-1].status != 'running': # костыльно немного,
        pass                                                # но иначе не выходит
    sleep(5)
    client.containers.prune()

def teardown_module(module):
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd':
            container.stop()
            container.remove()

def test_get_transport_from_params_pass():
    ssh = get_transport('ssh', 'localhost', 22022, 'root', 'pwd')
    assert isinstance(ssh, SSH_transport)

def test_get_transport_from_config_pass():
    ssh = get_transport('ssh')
    assert isinstance(ssh, SSH_transport)

def test_get_transport_except():
    with pytest.raises(TransportCreationError) as e_info:
        get_transport('noway')
    assert str(e_info).endswith('UnknownTransport')

class Test_SSH_transport:
    def test_connect_pass(self):
        with get_transport('ssh') as ssh:
            ssh.connect()

    def test_connect_wrong_auth(self):
        with get_transport('ssh', password = 'wrong') as ssh,\
            pytest.raises(AuthenticationError) as e_info:
            ssh.connect()
        assert str(e_info).endswith('Authentication failed')

    def test_connect_wrong_host(self):
        with get_transport('ssh', port = 666) as ssh, pytest.raises(TransportConnectionError) as e_info:
            ssh.connect()
        assert str(e_info).endswith("Couldn't connect to host")

    def test_execute_pass(self):
        with get_transport('ssh') as ssh:
            ssh.connect()
            assert isinstance(ssh.execute('ls /'), tuple)

    def test_execute_except(self):
        with get_transport('ssh', login = 'testuser', password = 'pass') as ssh,\
            pytest.raises(TransportError) as e_info:
            ssh.connect()
            ssh.execute('wrong_command')

    def test_get_file_pass(self):
        with get_transport('ssh') as ssh:
            ssh.connect()
            assert isinstance(ssh.get_file('/etc/passwd'), bytes)

    def test_get_file_except(self):
        with get_transport('ssh') as ssh, pytest.raises(TransportError) as e_info:
            ssh.connect()
            ssh.get_file('/wrong_file')
