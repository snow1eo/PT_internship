import sqlite3

from modules.database import DB_NAME, init_database
from modules.testing import run_tests, get_tests


def test_run_tests(change_dir):
    init_database()
    total_tests = len(get_tests())
    run_tests()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        tests_writed = len(curr.execute("SELECT * FROM scandata").fetchall())
    assert total_tests == tests_writed
