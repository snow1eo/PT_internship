import json
import os
import re
import sqlite3
from datetime import datetime

from modules.errors import ConfigError
from modules.transports import get_transport_config, get_transport_names, get_host_name

DB_NAME = 'sqlite3.db'
CFG_NAME = os.path.join('config', 'controls.json')

_controls = None
_initialized = False
_scan_id = None


def get_tests():
    check_config()
    return {
        re.findall(r'\d+', test)[0]: test.strip('.py')
        for test in os.listdir('scripts')
        if re.match(r'\d+_.+\.py', test)
    }


def get_controls():
    global _controls
    if not _controls:
        with open(CFG_NAME) as f:
            _controls = json.load(f)
    return _controls


def check_config():
    test_nums = [int(re.findall(r'\d+', test)[0]) for test in os.listdir('scripts')
                 if re.match(r'\d+_.+\.py', test)]
    cfg_nums = set(map(int, get_controls().keys()))
    if not set(test_nums).issubset(cfg_nums):
        raise ConfigError(CFG_NAME)


def get_scan_id():
    global _scan_id
    if not _scan_id:
        with sqlite3.connect(DB_NAME) as db:
            curr = db.cursor()
            _scan_id = curr.execute("""SELECT seq FROM sqlite_sequence
                WHERE name = 'scanning'""").fetchone()[0]
    return _scan_id


def init_database():
    check_config()
    if os.path.exists(DB_NAME):
        return
    controls = get_controls()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("""PRAGMA foreign_keys = ON""")
        curr.execute("""CREATE TABLE IF NOT EXISTS control(
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        requirement TEXT,
                        prescription TEXT)""")
        for id_, params in controls.items():
            curr.execute("INSERT INTO control VALUES (?, ?, ?, ?, ?)",
                         (id_, params['title'], params['descr'],
                          params['req'], params['prescription']))
        curr.execute("""CREATE TABLE IF NOT EXISTS transport(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        user TEXT NOT NULL,
                        port INTEGER NOT NULL,
                        scan_id INTEGER NOT NULL,
                        FOREIGN KEY (scan_id) REFERENCES scanning(id))""")
        curr.execute("""CREATE TABLE IF NOT EXISTS scanning(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        host TEXT NOT NULL,
                        start TEXT,
                        finish TEXT)""")
        curr.execute("""CREATE TABLE IF NOT EXISTS scandata(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ctrl_id INTEGER NOT NULL,
                        status INTEGER,
                        error TEXT,
                        scan_id INTEGER NOT NULL,
                        FOREIGN KEY (ctrl_id) REFERENCES control(id),
                        FOREIGN KEY (scan_id) REFERENCES scanning(id))""")
        curr.execute("""CREATE TABLE IF NOT EXISTS audit(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attribute TEXT,
                        value TEXT,
                        protocol TEXT,
                        scan_id INTEGER NOT NULL,
                        FOREIGN KEY (scan_id) REFERENCES scanning(id))""")


def reset_database():
    global _initialized
    global _controls
    global _scan_id
    _initialized = False
    _controls = None
    _scan_id = None
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_database()
    init_scanning()
    set_finish_time()


def add_control(ctrl_id, status, error):
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        curr.execute("INSERT INTO scandata VALUES (NULL, ?, ?, ?, ?)",
                     (ctrl_id, status, error, get_scan_id()))


def init_scanning():
    global _initialized
    if _initialized:
        return
    init_database()
    transport_names = get_transport_names()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("INSERT INTO scanning VALUES (NULL, ?, ?, NULL)",
                     (get_host_name(), str(datetime.now())))
        db.commit()
        for transport_name in transport_names:
            transport = get_transport_config(transport_name)
            curr.execute("INSERT INTO transport VALUES (NULL, ?, ?, ?, ?)",
                         (transport_name, transport.user, transport.port, get_scan_id()))
    _initialized = True


def set_finish_time():
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("UPDATE scanning SET finish = ? WHERE id = ?",
                     (str(datetime.now()), get_scan_id()))
