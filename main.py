#!/usr/bin/env python3

import importlib
import os, sys
import sqlite3
import re
import json
from modules.reporting import generate_report

db_name = 'sqlite3.db'

class ConfigError(Exception):
    pass

def check_config():
    if 'controls.json' not in os.listdir('./'):
        raise ConfigError("controls.json doesn't exist")
    test_nums = [int(test[:3]) for test in os.listdir('scripts')\
                            if re.match(r'\d{3}_.+\.py', test)]
    if len(test_nums) != len(set(test_nums)):
        raise ConfigError('duplicate test numbers')
    with open('controls.json') as f:
        cfg_nums = [int(ctrl[0]) for ctrl in json.load(f)]
    if len(cfg_nums) != len(set(cfg_nums)):
        raise ConfigError('duplicate items')
    if set(cfg_nums) != set(test_nums):
        raise ConfigError("config doesn't match scripts")

def init_database():
    delete_database()
    db = sqlite3.connect(db_name)
    curr = db.cursor()
    curr.execute("""CREATE TABLE IF NOT EXISTS
        control(id INTEGER PRIMARY KEY, descr TEXT)""")
    with open('controls.json') as f:
        controls = json.load(f)
    for control in controls:
        curr.execute("""INSERT INTO control VALUES
            ({ctrl_id}, "{descr}")""".format(
                ctrl_id = control[0], descr = control[1]))
    curr.execute("""CREATE TABLE IF NOT EXISTS
        scandata(id INTEGER PRIMARY KEY, descr TEXT, status INTEGER)""")
    db.commit()
    db.close()

def delete_database():
    if db_name in os.listdir('./'):
        os.remove(db_name)

def run_tests():
    tests = [test.strip('.py') for test in os.listdir('scripts')\
                            if re.match(r'\d{3}_.+\.py', test)]

    for test in tests:
        ctrl_id = re.findall(r'\d+', test)[0]
        try:
            test_mod = importlib.import_module('.'+test, package = 'scripts')
            status = test_mod.main()
        except Exception as e_info:
            print('ERROR: {}'.format(e_info))
            status = 5
        add_control(ctrl_id, status)

def add_control(ctrl_id, status):
    db = sqlite3.connect(db_name)
    curr = db.cursor()
    descr = curr.execute("""SELECT descr FROM control
        WHERE id={}""".format(ctrl_id)).fetchall()
    if descr:
        descr = descr[0][0]
    else:
        raise ConfigError("description for {} not found"\
            .format(ctrl_id))
    curr.execute("""INSERT INTO scandata VALUES
        ({id_}, "{descr}", {status})""".format(
            id_ = ctrl_id, descr = descr, status = status))
    db.commit()
    db.close()

if __name__ == '__main__':
    check_config()
    init_database()
    run_tests()
    generate_report()
    delete_database()