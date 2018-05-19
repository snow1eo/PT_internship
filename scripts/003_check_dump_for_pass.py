import sqlite3

from passlib.hash import cisco_type7

from modules.database import DB_NAME
from modules.errors import TransportConnectionError, RemoteHostCommandError
from modules.statuses import Status
from modules.transports import get_transport

TEST_NUM = 3


def main():
    try:
        ssh = get_transport('SSH')
        data = ssh.execute_show('show mem | strings | grep password')
        if not data:
            return Status.COMPLIANT, None
        else:
            # Пока только 1 вариант обрабатывается
            data = tuple(map(lambda x: x.split(), data.split('\n')))[0]
            login = data[0]  # Это же логин?
            password = cisco_type7.decode(data[4])
            with sqlite3.connect(DB_NAME) as db:
                curr = db.cursor()
                curr.execute("UPDATE control SET prescription = ? WHERE id = ?",
                             ("Found credentials: {}: {}".format(
                                 login, password), TEST_NUM))
            return Status.NOT_COMPLIANT, None
    except (TransportConnectionError, RemoteHostCommandError):
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception as e_info:
        return Status.ERROR, str(e_info)
