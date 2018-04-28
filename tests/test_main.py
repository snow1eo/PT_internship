import pytest
import docker
import sys, os
from shutil import rmtree, copytree
import sqlite3
import json
if os.getcwd().endswith('tests'):
    os.chdir('..')
sys.path.append(os.getcwd())
from main import *

required_tables = {'control', 'scandata'}

def setup_module(module):
    if '.test_tmp' in os.listdir():
        rmtree('.test_tmp')
    copytree('.', '.test_tmp')
    os.chdir('.test_tmp')

def teardown_module(module):
    os.chdir('..')
    if '.test_tmp' in os.listdir():
        rmtree('.test_tmp')

def setup_function():
    init_database()

def teardown_function():
    delete_database()

@pytest.mark.first
def test_check_config():
    # TODO (somwhere. Probably)
    pass

@pytest.mark.second
def test_init_database():
    init_database()
    assert db_name in os.listdir()
    db = sqlite3.connect(db_name)
    curr = db.cursor()
    curr.execute("SELECT name FROM sqlite_master where type = 'table'""")
    tables = curr.fetchall()
    tables = list(map(list, tables)) # Converting a list
    tables = set(sum(tables, []))    # to a linear set
    assert tables == required_tables
    assert not curr.execute("""SELECT * FROM scandata""").fetchall()
    with open('controls.json') as f:
        # Converting to form to compare
        required_controls = set(map(lambda x: (int(x[0]), x[1], x[2]), \
            map(tuple, json.load(f))))
    controls = set(curr.execute("""SELECT * FROM control""").fetchall())
    assert controls == required_controls

def test_run_tests():
    # TODO 2
    pass

def test_add_control_pass():
    ctrls = [['200', 'some desription', 'some info']]
    with open('controls.json', 'w') as f:
        json.dump(ctrls, f)
    init_database()
    add_control(200, 3)
    db = sqlite3.connect(db_name)
    curr = db.cursor()
    rec = curr.execute("""SELECT * FROM scandata""").fetchall()
    assert rec[-1][1:] == (200, 3)

def test_add_control_foreign_key_err():
    with pytest.raises(ConfigError) as e_info:
        add_control(404, 3)
    assert e_info