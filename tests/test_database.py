import json
import os
import sqlite3
import sys
from shutil import rmtree, copytree

import pytest

if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from modules.database import CFG_NAME, DB_NAME, \
    check_config, init_database, add_control


TEST_DIR = '.test_tmp'
REQUIRED_TABLES = {'control', 'scandata'}
TEST_NUM_PASS = 200   # any value for pass test
TEST_NUM_ERR = 404    # any value, which doesn't exist in DB
TEST_STATUS = 3       # any value for test


def setup_module():
    if TEST_DIR in os.listdir():
        rmtree(TEST_DIR)
    copytree('.', TEST_DIR)
    os.chdir(TEST_DIR)


def teardown_module():
    os.chdir('..')
    if TEST_DIR in os.listdir():
        rmtree(TEST_DIR)


@pytest.mark.first
def test_check_config():
    # TODO (some time or other. Probably)
    check_config()


@pytest.mark.second
def test_init_database():
    init_database()
    assert DB_NAME in os.listdir()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("""SELECT name FROM sqlite_master where type = 'table'""")
        tables = curr.fetchall()
        tables = list(map(list, tables))  # Converting a list
        tables = set(sum(tables, []))     # to a linear set
        assert tables == REQUIRED_TABLES
        assert not curr.execute("""SELECT * FROM scandata""").fetchall()
        with open(CFG_NAME) as f:
            # Converting to form to compare
            required_controls = set(map(lambda x: (int(x[0]), *x[1:]),
                                        map(tuple, json.load(f))))
        controls = set(curr.execute("""SELECT * FROM control""").fetchall())
        assert controls == required_controls


def test_add_control_pass():
    controls = [[str(TEST_NUM_PASS), 'title', 'description', 'requirement']]
    with open(CFG_NAME, 'w') as f:
        json.dump(controls, f)
    init_database()
    add_control(TEST_NUM_PASS, TEST_STATUS)
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        rec = curr.execute("""SELECT * FROM scandata""").fetchone()
    assert rec[1:] == (TEST_NUM_PASS, TEST_STATUS)


def test_add_control_foreign_key_err():
    init_database()
    with pytest.raises(sqlite3.IntegrityError) as e_info:
        add_control(TEST_NUM_ERR, TEST_STATUS)
    assert e_info
