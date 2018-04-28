import json
import sqlite3
import os

db_name = 'sqlite3.db'

class DatabaseError(Exception):
    pass

def init_database():
    delete_database()
    db = sqlite3.connect(db_name)
    curr = db.cursor()
    curr.execute("PRAGMA foreign_keys = ON")
    curr.execute("""CREATE TABLE IF NOT EXISTS
        control(id INTEGER PRIMARY KEY, descr TEXT, info TEXT)""")
    with open('controls.json') as f:
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