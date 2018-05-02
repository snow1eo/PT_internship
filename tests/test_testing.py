import os
import pytest
import sqlite3
import sys
import re
from shutil import rmtree, copytree

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.testing import run_tests, get_tests
from modules.database import DB_NAME, init_database


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
