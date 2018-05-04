import os
import re
import sqlite3
from shutil import rmtree, copytree
from time import sleep

import pytest

from modules.database import DB_NAME, init_database
from modules.testing import run_tests, get_tests

TEST_DIR = '.test_tmp'


def setup_module():
    if TEST_DIR in os.listdir():
        rmtree(TEST_DIR)
    copytree('.', TEST_DIR)
    os.chdir(TEST_DIR)
    init_database()


def teardown_module():
    os.chdir('..')
    if TEST_DIR in os.listdir():
        rmtree(TEST_DIR)
    # Вот здесь наиболее критично дать базе опомниться
    sleep(3)

@pytest.mark.first
def test_get_tests():
    tests = get_tests()
    assert isinstance(tests, dict)
    assert len(tests) == len([t for t in os.listdir('scripts') if \
                              re.match(r'\d+_.+\.py', t)])

def test_run_tests():
    total_tests = len(get_tests())
    run_tests()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        tests_writed = len(curr.execute("SELECT * FROM scandata").fetchall())
    assert total_tests == tests_writed
