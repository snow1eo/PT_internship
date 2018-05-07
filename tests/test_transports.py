import pytest

from modules.errors import UnknownTransport, AuthenticationError, SSHFileNotFound, \
    TransportConnectionError, TransportError, MySQLError, UnknownDatabase
from modules.transports import get_transport, get_transport_config, \
    SSHTransport, MySQLTransport

PATH = 'tests'
WRONG_PORT = -1
port_ssh = get_transport_config('SSH').port
port_sql = get_transport_config('MySQL').port
env_sql = get_transport_config('MySQL').environment


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

    def test_persistent_connection(self):
        assert get_transport('MySQL') is get_transport('MySQL')

    def test_connect_wrong_auth(self):
        with pytest.raises(AuthenticationError):
            with get_transport('MySQL', password='wrong'):
                pass

    def test_connect_wrong_host(self):
        with pytest.raises(TransportConnectionError):
            with get_transport('MySQL', port=WRONG_PORT):
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

    def test_persistent_connection(self):
        assert get_transport('SSH') is get_transport('SSH')

    def test_connect_wrong_auth(self):
        with pytest.raises(AuthenticationError):
            with get_transport('SSH', password='wrong'):
                pass

    def test_connect_wrong_host(self):
        with pytest.raises(TransportConnectionError):
            with get_transport('SSH', port=WRONG_PORT):
                pass

    def test_execute_pass(self):
        with get_transport('SSH') as ssh:
            assert isinstance(ssh.execute('ls /'), tuple)

    def test_execute_except(self):
        with get_transport('SSH') as ssh:
            with pytest.raises(TransportError):
                ssh.execute('wrong_command')

    def test_execute_permission_denied_except(self):
        with get_transport('SSH', login='testuser', password='pass') as ssh:
            with pytest.raises(TransportError):
                ssh.execute('wrong_command')

    def test_get_file_pass(self):
        with get_transport('SSH') as ssh:
            assert isinstance(ssh.get_file('/etc/passwd'), bytes)

    def test_get_file_except(self):
        with get_transport('SSH') as ssh:
            with pytest.raises(SSHFileNotFound):
                ssh.get_file('/wrong_file')
