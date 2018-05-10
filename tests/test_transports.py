import pytest

from modules.errors import UnknownTransport, AuthenticationError, SSHFileNotFound, \
    TransportConnectionError, TransportError, MySQLError, UnknownDatabase
from modules.transports import get_transport, get_transport_config, \
    SSHTransport, MySQLTransport

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
                        user='root',
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
        sql = get_transport('MySQL')
        sql.sqlexec('SHOW DATABASES')

    def test_with_connect(self):
        with get_transport('MySQL') as sql:
            sql.sqlexec('SHOW DATABASES')

    def test_persistent_connection(self):
        assert get_transport('MySQL') is get_transport('MySQL')

    def test_connect_wrong_auth(self):
        with pytest.raises(AuthenticationError):
            get_transport('MySQL', password='wrong')

    def test_connect_wrong_host(self):
        with pytest.raises(TransportConnectionError):
            get_transport('MySQL', port=WRONG_PORT)

    def test_connect_wrong_db(self):
        with pytest.raises(UnknownDatabase):
            sql = get_transport('MySQL')
            sql.connect('wrong_database')

    def test_sqlexec_request(self):
        sql = get_transport('MySQL')
        sql.sqlexec('CREATE DATABASE IF NOT EXISTS test_db')
        sql.connect('test_db')
        sql.sqlexec("""CREATE TABLE IF NOT EXISTS test (
                    name VARCHAR(20), owner VARCHAR(20))""")
        sql.sqlexec("INSERT INTO test VALUES ('Dolly', 'Me')")
        data = sql.sqlexec('SELECT * FROM test')
        assert data == [{'name': 'Dolly', 'owner': 'Me'}]

    def test_sqlexec_wrong_request(self):
        sql = get_transport('MySQL')
        with pytest.raises(MySQLError):
            sql.sqlexec('WRONG REQUEST')


class TestSSHTransport:
    def test_connect_pass(self):
        ssh = get_transport('SSH')
        ssh.execute('ls')

    def test_with_connect(self):
        with get_transport('SSH') as ssh:
            ssh.execute('ls')

    def test_persistent_connection(self):
        assert get_transport('SSH') is get_transport('SSH')

    def test_connect_wrong_auth(self):
        with pytest.raises(AuthenticationError):
            get_transport('SSH', password='wrong')

    def test_connect_wrong_host(self):
        with pytest.raises(TransportConnectionError):
            get_transport('SSH', port=WRONG_PORT)

    def test_execute_pass(self):
        ssh = get_transport('SSH')
        assert isinstance(ssh.execute('ls /'), tuple)

    def test_execute_except(self):
        ssh = get_transport('SSH')
        with pytest.raises(TransportError):
            ssh.execute('wrong_command')

    def test_execute_permission_denied_except(self):
        ssh = get_transport('SSH', user='testuser', password='pass')
        with pytest.raises(TransportError):
            ssh.execute('cat /etc/shadow')

    def test_get_file_pass(self):
        ssh = get_transport('SSH')
        assert isinstance(ssh.get_file('/etc/passwd'), bytes)

    def test_get_file_except(self):
        ssh = get_transport('SSH')
        with pytest.raises(SSHFileNotFound):
            ssh.get_file('/wrong_file')
