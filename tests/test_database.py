import json
import os
import re
import sqlite3
from shutil import rmtree

import pytest

from modules.database import CFG_NAME, DB_NAME, check_config, reset_database, \
    init_database, add_control, get_controls, get_tests, init_scanning, set_finish_time

REQUIRED_TABLES = frozenset({'transport', 'control', 'scandata',
                             'scanning', 'sqlite_sequence', 'audit'})
TEST_NUM_PASS = 200  # any value for pass test
TEST_NUM_ERR = 404  # any value, which doesn't exist in DB
TEST_STATUS = 3  # any value for test
ERROR = 'some error message'


@pytest.mark.first
def test_get_tests(change_dir):
    tests = get_tests()
    assert isinstance(tests, dict)
    assert len(tests) == len([t for t in os.listdir('scripts') if
                              re.match(r'\d+_.+\.py', t)])


@pytest.mark.second
def test_check_config(change_dir):
    check_config()


def test_init_database(change_dir, create_new_database):
    init_database()
    assert os.path.exists(DB_NAME)
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("SELECT name FROM sqlite_master where type = 'table'")
        tables = curr.fetchall()
        tables = list(map(list, tables))  # Converting a list
        tables = set(sum(tables, []))  # to a linear set
        assert tables == REQUIRED_TABLES
        assert not curr.execute("""SELECT * FROM scandata""").fetchall()
        # Converting to form to compare
        required_controls = {int(id_): {'title': p['title'], 'descr': p['descr'],
                                        'req': p['req'], 'prescription': p['prescription']}
                             for id_, p in get_controls().items()}
        controls = {id_: {'title': title, 'descr': descr, 'req': req,
                          'prescription': presc} for
                    id_, title, descr, req, presc in
                    curr.execute("SELECT * FROM control").fetchall()}
        assert controls == required_controls


def test_init_scanning(change_dir, create_new_database):
    init_scanning()


def test_set_finish_time(change_dir, create_new_database):
    set_finish_time()


def test_add_control_err_pass(change_dir, create_new_database):
    controls = {
        str(TEST_NUM_PASS): {
            "title": "",
            "descr": "",
            "req": "",
            "prescription": "",
            "env": {}
        }}
    with open(CFG_NAME, 'w') as f:
        json.dump(controls, f)
    # очистка папки scripts для корректности конфига
    rmtree('scripts')
    os.mkdir('scripts')
    reset_database()
    add_control(TEST_NUM_PASS, TEST_STATUS, ERROR)
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        rec = curr.execute("""SELECT * FROM scandata""").fetchone()
    assert rec[1:-1] == (TEST_NUM_PASS, TEST_STATUS, ERROR)


def test_add_control_no_err_pass(change_dir, create_new_database):
    controls = {
        str(TEST_NUM_PASS): {
            "title": "",
            "descr": "",
            "req": "",
            "prescription": "",
            "env": {}
        }}
    with open(CFG_NAME, 'w') as f:
        json.dump(controls, f)
    # очистка папки scripts для корректности конфига
    rmtree('scripts')
    os.mkdir('scripts')
    reset_database()
    add_control(TEST_NUM_PASS, TEST_STATUS, None)
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        rec = curr.execute("""SELECT * FROM scandata""").fetchone()
    assert rec[1:-1] == (TEST_NUM_PASS, TEST_STATUS, None)


def test_add_control_foreign_key_err(change_dir, create_new_database):
    rmtree('scripts')
    os.mkdir('scripts')
    reset_database()
    with pytest.raises(sqlite3.IntegrityError):
        add_control(TEST_NUM_ERR, TEST_STATUS, ERROR)
