import sqlite3

from modules.database import DB_NAME
from modules.testing import run_tests, get_tests


def test_run_tests(run_docker, change_dir, create_new_database):
    total_tests = len(get_tests())
    run_tests()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        tests_written = len(curr.execute("SELECT * FROM scandata").fetchall())
    assert total_tests == tests_written
