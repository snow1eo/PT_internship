import json
import sqlite3
import os
import re

cfg_name = 'controls.json'
db_name = 'sqlite3.db'

class DatabaseError(Exception):
    pass

class ConfigError(Exception):
    pass

def check_config():
    if cfg_name not in os.listdir('./'):
        raise ConfigError("controls.json doesn't exist")
    test_nums = [int(re.findall(r'\d+', test)[0]) for test in os.listdir('scripts')\
                            if re.match(r'\d+_.+\.py', test)]
    if len(test_nums) != len(set(test_nums)):
        raise ConfigError('duplicate test numbers')
    with open(cfg_name) as f:
        cfg_nums = [int(ctrl[0]) for ctrl in json.load(f)]
    if len(cfg_nums) != len(set(cfg_nums)):
        raise ConfigError('duplicate items')
    if not set(test_nums).issubset(set(cfg_nums)):
        raise ConfigError("config doesn't match scripts")

def init_database():
    delete_database()
    db = sqlite3.connect(db_name)
    curr = db.cursor()
    curr.execute("PRAGMA foreign_keys = ON")
    curr.execute("""CREATE TABLE IF NOT EXISTS
        control(id INTEGER PRIMARY KEY, descr TEXT, info TEXT)""")
    with open(cfg_name) as f:
        controls = json.load(f)
    for control in controls:
        curr.execute('INSERT INTO control VALUES (?, ?, ?)', control)
    curr.execute("""CREATE TABLE IF NOT EXISTS scandata(
                    id INTEGER PRIMARY KEY,
                    ctrl_id INTEGER NOT NULL,
                    status INTEGER,
                    FOREIGN KEY (ctrl_id) REFERENCES control(id))
                    """)
    db.commit()
    db.close()

def delete_database():
    if db_name in os.listdir('./'):
        os.remove(db_name)

def add_control(ctrl_id, status):
    db = sqlite3.connect(db_name)
    curr = db.cursor()
    if not curr.execute('SELECT * FROM control WHERE id=?', (ctrl_id,)).fetchall():
        raise DatabaseError('foreign key error')
    curr.execute('INSERT INTO scandata VALUES (NULL, ?, ?)', (ctrl_id, status))
    db.commit()
    db.close()