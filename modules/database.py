import json
import os
import re
import sqlite3

from modules.errors import ConfigError, DuplicateTestNumError

DB_NAME = 'sqlite3.db'
CFG_NAME = os.path.join('config', 'controls.json')


_controls = None


def get_controls():
    global _controls
    if not _controls:
        with open(CFG_NAME) as f:
            _controls = json.load(f)
    return _controls


def check_config():
    test_nums = [int(re.findall(r'\d+', test)[0]) for test in os.listdir('scripts')
                 if re.match(r'\d+_.+\.py', test)]
    if len(test_nums) != len(set(test_nums)):
        raise DuplicateTestNumError("duplicate test numbers in 'scripts'")
    cfg_nums = set(map(int, get_controls().keys()))
    if not set(test_nums).issubset(cfg_nums):
        raise ConfigError("{} doesn't match scripts".format(CFG_NAME))


def init_database():
    delete_database()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        curr.execute("""CREATE TABLE IF NOT EXISTS control(
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        description TEXT,
                        requirement)""")
        controls = get_controls()
        for id_, params in controls.items():
            curr.execute("INSERT INTO control VALUES (?, ?, ?, ?)",
                    (id_, params['title'], params['descr'], params['req']))
        curr.execute("""CREATE TABLE IF NOT EXISTS scandata(
                    id INTEGER PRIMARY KEY,
                    ctrl_id INTEGER NOT NULL,
                    status INTEGER,
                    FOREIGN KEY (ctrl_id) REFERENCES control(id))""")


def delete_database():
    global _controls
    _controls = None
    if DB_NAME in os.listdir('./'):
        os.remove(DB_NAME)


def add_control(ctrl_id, status):
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        curr.execute("INSERT INTO scandata VALUES (NULL, ?, ?)",
            (ctrl_id, status))
