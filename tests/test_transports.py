import sqlite3

import pytest

from modules.errors import UnknownTransport, AuthenticationError, SSHFileNotFound, \
    TransportConnectionError, TransportError, MySQLError, UnknownDatabase
from modules.transports import get_transport, get_transport_config, \
    SSHTransport, MySQLTransport, CACHE_DB_NAME

WRONG_PORT = -1
port_ssh = get_transport_config('SSH').port
port_sql = get_transport_config('MySQL').port
env_sql = get_transport_config('MySQL').environment


def test_get_ssh_transport_from_params_pass(run_docker):
    ssh = get_transport('SSH', 'localhost', port_ssh, 'root', 'pwd')
    assert isinstance(ssh, SSHTransport)


def test_get_ssh_transport_from_config_pass(run_docker):
    ssh = get_transport('SSH')
    assert isinstance(ssh, SSHTransport)


def test_get_mysql_transport_from_params_pass(run_docker):
    sql = get_transport(transport_name='MySQL',
                        host='localhost',
                        port=port_sql,
                        user='root',
                        password=env_sql['MYSQL_ROOT_PASSWORD'])
    assert isinstance(sql, MySQLTransport)


def test_get_mysql_transport_from_config_pass(run_docker):
    sql = get_transport('MySQL')
    assert isinstance(sql, MySQLTransport)


def test_get_transport_except(run_docker):
    with pytest.raises(UnknownTransport):
        get_transport('noway')


class TestMySQLTransport:
    def test_connect_pass(self, run_docker):
        sql = get_transport('MySQL')
        sql.sqlexec('SHOW DATABASES')

    def test_with_connect(self, run_docker):
        with get_transport('MySQL') as sql:
            sql.sqlexec('SHOW DATABASES')

    def test_persistent_connection(self, run_docker):
        assert get_transport('MySQL') is get_transport('MySQL')

    def test_connect_wrong_auth(self, run_docker):
        with pytest.raises(AuthenticationError):
            get_transport('MySQL', password='wrong')

    def test_connect_wrong_host(self, run_docker):
        with pytest.raises(TransportConnectionError):
            get_transport('MySQL', port=WRONG_PORT)

    def test_connect_wrong_db(self, run_docker):
        with pytest.raises(UnknownDatabase):
            sql = get_transport('MySQL')
            sql.connect('wrong_database')

    def test_sqlexec_request(self, run_docker):
        sql = get_transport('MySQL')
        sql.sqlexec('CREATE DATABASE IF NOT EXISTS test_db')
        sql.connect('test_db')
        sql.sqlexec("DROP TABLE IF EXISTS test")
        sql.sqlexec("""CREATE TABLE IF NOT EXISTS test(
                    name VARCHAR(20), owner VARCHAR(20))""")
        sql.sqlexec("INSERT INTO test VALUES ('Dolly', 'Me')")
        data = sql.sqlexec('SELECT * FROM test')
        assert data == [{'name': 'Dolly', 'owner': 'Me'}]

    def test_sqlexec_wrong_request(self, run_docker):
        sql = get_transport('MySQL')
        with pytest.raises(MySQLError):
            sql.sqlexec('WRONG REQUEST')

    def test_get_global_variables_pass(self, run_docker, change_dir):
        sql = get_transport('MySQL')
        assert sql.get_global_variables()
        with sqlite3.connect(CACHE_DB_NAME) as db:
            curr = db.cursor()
            assert curr.execute("""SELECT * FROM variable""")


class TestSSHTransport:
    def test_connect_pass(self, run_docker):
        ssh = get_transport('SSH')
        ssh.execute('ls')

    def test_with_connect(self, run_docker):
        with get_transport('SSH') as ssh:
            ssh.execute('ls')

    def test_persistent_connection(self, run_docker):
        assert get_transport('SSH') is get_transport('SSH')

    def test_connect_wrong_auth(self, run_docker):
        with pytest.raises(AuthenticationError):
            get_transport('SSH', password='wrong')

    def test_connect_wrong_host(self, run_docker):
        with pytest.raises(TransportConnectionError):
            get_transport('SSH', port=WRONG_PORT)

    def test_execute_pass(self, run_docker):
        ssh = get_transport('SSH')
        assert isinstance(ssh.execute('ls /'), tuple)

    def test_execute_except(self, run_docker):
        ssh = get_transport('SSH')
        with pytest.raises(TransportError):
            ssh.execute('wrong_command')

    def test_get_file_pass(self, run_docker):
        ssh = get_transport('SSH')
        assert isinstance(ssh.get_file('/etc/passwd'), bytes)

    def test_get_file_except(self, run_docker):
        ssh = get_transport('SSH')
        with pytest.raises(SSHFileNotFound):
            ssh.get_file('/wrong_file')


class TestSNMPTransport:
    def test_connect(self, run_docker):
        get_transport('SNMP')

    def test_get_snmpdata(self, run_docker):
        snmp = get_transport('SNMP')
        assert snmp.get_snmpdata('.1.3.6.1.2.1.1.1.0')
