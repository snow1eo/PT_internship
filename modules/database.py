import json
import sqlite3
import os
import re

CFG_NAME = 'controls.json'
DB_NAME = 'sqlite3.db'

class DatabaseError(Exception):
    pass

class ForeignKeyError(DatabaseError):
    pass

class ConfigError(Exception):
    pass

class DuplicateTestNumError(ConfigError):
    pass

def check_config():
    if CFG_NAME not in os.listdir('./'):
        raise ConfigError("controls.json doesn't exist")
    test_nums = [int(re.findall(r'\d+', test)[0]) for test in os.listdir('scripts')\
                            if re.match(r'\d+_.+\.py', test)]
    if len(test_nums) != len(set(test_nums)):
        raise DuplicateTestNumError("duplicate test numbers in 'scripts' directory")
    with open(CFG_NAME) as f:
        cfg_nums = [int(ctrl[0]) for ctrl in json.load(f)]
    if len(cfg_nums) != len(set(cfg_nums)):
        raise DuplicateTestNumError("duplicate tests numbers in '{}'".format(CFG_NAME))
    if not set(test_nums).issubset(set(cfg_nums)):
        raise ConfigError("config doesn't match scripts")

def init_database():
    delete_database()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        curr.execute("""CREATE TABLE IF NOT EXISTS
                control(id INTEGER PRIMARY KEY, descr TEXT, info TEXT)""")
        with open(CFG_NAME) as f:
            controls = json.load(f)
        for control in controls:
            curr.execute('INSERT INTO control VALUES (?, ?, ?)', control)
        curr.execute("""CREATE TABLE IF NOT EXISTS scandata(
                    id INTEGER PRIMARY KEY,
                    ctrl_id INTEGER NOT NULL,
                    status INTEGER,
                    FOREIGN KEY (ctrl_id) REFERENCES control(id))""")

def delete_database():
    if DB_NAME in os.listdir('./'):
        os.remove(DB_NAME)

def add_control(ctrl_id, status):
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        curr.execute('INSERT INTO scandata(id, ctrl_id, status) VALUES (NULL, ?, ?)', (ctrl_id, status))
