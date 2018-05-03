from time import sleep

import docker
import pytest

from modules.transports import get_config, get_transport, SSHTransport, \
    MySQLTransport, UnknownTransport, AuthenticationError, TransportConnectionError, TransportError, MySQLError, UnknownDatabase

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


def test_get_ssh_transport_from_params_pass():
    ssh = get_transport('SSH', 'localhost', port_ssh, 'root', 'pwd')
    assert isinstance(ssh, SSHTransport)


def test_get_ssh_transport_from_config_pass():
    ssh = get_transport('SSH')
    assert isinstance(ssh, SSHTransport)


def test_get_mysql_transport_from_params_pass():
    sql = get_transport(transport_name='MySQL',
                        host='localhost',
                        port=port_sql,
                        login='root',
                        password=env_sql['MYSQL_ROOT_PASSWORD'])
    assert isinstance(sql, MySQLTransport)


def test_get_mysql_transport_from_config_pass():
    sql = get_transport('MySQL')
    assert isinstance(sql, MySQLTransport)


def test_get_transport_except():
    with pytest.raises(UnknownTransport):
        get_transport('noway')


class TestMySQLTransport:
    def test_connect_pass(self):
        with get_transport('MySQL'):
            pass

    def test_connect_wrong_auth(self):
        with pytest.raises(AuthenticationError):
            with get_transport('MySQL', password='wrong'):
                pass

    def test_connect_wrong_host(self):
        with pytest.raises(TransportConnectionError):
             with get_transport('MySQL', port=666):
                pass

    def test_connect_wrong_db(self):
        with pytest.raises(UnknownDatabase):
            with get_transport('MySQL') as sql:
                sql.connect('wrong_database')

    def test_sqlexec_pass(self):
        with get_transport('MySQL') as sql:
            sql.sqlexec('SHOW DATABASES')

    def test_sqlexec_request(self):
        with get_transport('MySQL') as sql:
            sql.sqlexec('CREATE DATABASE IF NOT EXISTS test_db')
            sql.close()
            sql.connect('test_db')
            sql.sqlexec("""CREATE TABLE IF NOT EXISTS test (
                        name VARCHAR(20), owner VARCHAR(20))""")
            sql.sqlexec("INSERT INTO test VALUES ('Dolly', 'Me')")
            data = sql.sqlexec('SELECT * FROM test')
        assert data == [{'name': 'Dolly', 'owner': 'Me'}]

    def test_sqlexec_wrong_request(self):
        with get_transport('MySQL') as sql:
            with pytest.raises(MySQLError):
                sql.sqlexec('WRONG REQUEST')


class TestSSHTransport:
    def test_connect_pass(self):
        with get_transport('SSH'):
            pass

    def test_connect_wrong_auth(self):
        with pytest.raises(AuthenticationError):
            with get_transport('SSH', password='wrong'):
                pass

    def test_connect_wrong_host(self):
        with pytest.raises(TransportConnectionError):
            with get_transport('SSH', port=666):
                pass

    def test_execute_pass(self):
        with get_transport('SSH') as ssh:
            assert isinstance(ssh.execute('ls /'), tuple)

    def test_execute_except(self):
        with get_transport('SSH', login='testuser', password='pass') as ssh:
            with pytest.raises(TransportError):
                ssh.execute('wrong_command')

    def test_get_file_pass(self):
        with get_transport('SSH') as ssh:
            assert isinstance(ssh.get_file('/etc/passwd'), bytes)

    def test_get_file_except(self):
        with get_transport('SSH') as ssh, pytest.raises(TransportError):
            ssh.get_file('/wrong_file')
