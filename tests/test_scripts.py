import pytest
import docker
import sys, os
import importlib
import sqlite3

if os.getcwd().endswith('tests'):
    os.chdir('..')
from modules.transports import *
from main import *

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

def test_000_file_exist_1():
    ssh = get_transport('ssh')
    ssh.connect()
    ssh.execute('touch /testfile')
    mod = importlib.import_module('.000_test_file_exist', package = 'scripts')
    assert mod.main() == 1

def test_000_file_exist_2():
    ssh = get_transport('ssh')
    ssh.connect()
    try:
        ssh.execute('rm -f /testfile')
    except:
        pass
    mod = importlib.import_module('.000_test_file_exist', package = 'scripts')
    assert mod.main() == 2

def test_000_file_exist_3():
    containers = docker.from_env().containers.list()
    for container in containers:
        if container.name == 'cont_ubuntu_sshd':
            container.stop()
            mod = importlib.import_module('.000_test_file_exist', package = 'scripts')
            status = mod.main()
            container.start()
    assert status == 3

def test_000_file_exist_4():
    pass
    # TODO (HOW?)