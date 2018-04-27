import pytest
import docker
import sys, os
if os.getcwd().endswith('tests'):
    os.chdir('..')
from modules.transports import *

def setup_module(module):

    path = r'./tests/'
    dockerfile = r'./Dockerfile'

    client = docker.from_env()
    images = client.images.build(path = path, dockerfile = dockerfile)
    try:
        cont = client.containers.run(image  = images[0],
                                     detach = True,
                                     ports  = {'22/tcp' : 22022},
                                     name   = 'cont_ubuntu_sshd')
    except Exception as e:
        print(e)
    client.containers.prune()

def teardown_module(module):
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd':
            container.stop()
            container.remove()

def test_pass_get_transport_from_params():
    ssh = get_transport('ssh', 'localhost', 22022, 'root', 'pwd')
    assert isinstance(ssh, SSH_transport)

def test_pass_get_transport_from_config():
    ssh = get_transport('ssh')
    assert isinstance(ssh, SSH_transport)

def test_except_get_transport():
    with pytest.raises(TransportError) as e_info:
        get_transport('noway')
    assert str(e_info).endswith('UnknownTransport')

class Test_SSH_transport:
    def test_pass_connect(self):
        ssh = get_transport('ssh')
        ssh.connect()
        assert True

    def test_connect_wrong_auth(self):
        ssh = get_transport('ssh', password = 'wrong')
        with pytest.raises(TransportConnectionError) as e_info:
            ssh.connect()
        assert str(e_info).endswith('Authentication failed')

    def test_connect_wrong_host(self):
        ssh = get_transport('ssh', port = 666)
        with pytest.raises(TransportConnectionError) as e_info:
            ssh.connect()
        assert str(e_info).endswith("Couldn't connect to host")

    def test_pass_execute(self):
        ssh = get_transport('ssh')
        ssh.connect()
        assert isinstance(ssh.execute('ls /'), tuple)
        ssh.close()

    def test_except_execute(self):
        ssh = get_transport('ssh', login = 'testuser', password = 'pass')
        ssh.connect()
        with pytest.raises(TransportError) as e_info:
            ssh.execute('wrong_command')
        assert True

    def test_pass_get_file(self):
        ssh = get_transport('ssh')
        ssh.connect()
        assert isinstance(ssh.get_file('/etc/passwd'), bytes)
        ssh.close()

    def test_except_get_file(self):
        ssh = get_transport('ssh')
        ssh.connect()
        with pytest.raises(TransportError) as e_info:
            ssh.get_file('/wrong_file')
        ssh.close()
        assert True