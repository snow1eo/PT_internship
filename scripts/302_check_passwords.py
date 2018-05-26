import sys
import traceback

from modules.errors import TransportConnectionError
from modules.functions import mysql_hash
from modules.statuses import Status
from modules.transports import get_transport


def main():
    try:
        sql = get_transport('MySQL')
        users = sql.load_table('mysql.user')
        weak = set()
        for user in users:
            if pass_is_weak(user['User'], user['Password']):
                weak.add(user['User'])
        if not weak:
            return Status.COMPLIANT, None
        else:
            return Status.NOT_COMPLIANT, \
                   "Users have weak passwords: {}".format(', '.join(weak))
    except TransportConnectionError:
        return Status.NOT_APPLICABLE, 'No connection'
    except Exception:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        return Status.ERROR, traceback.format_exception(*exc_info)[-1]


def pass_is_weak(user, password):
    return password == mysql_hash(user) or \
           password == mysql_hash('pwd123')
