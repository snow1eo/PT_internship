import sqlite3

from modules.database import DB_NAME
from modules.transports import get_transport

def audit():
    snmp = get_transport('SNMP')
    sysDescr_data = snmp.get_snmpdata('sysDescr')['sysDescr'].split('\r\n')
    # TODO some parsing
    attributes = dict(
        vendor='somevendor',
        platform='someplatform',
        software_version='v2')
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        scan_id = curr.execute("SELECT seq FROM sqlite_sequence WHERE name = 'scanning'").fetchone()[0]
        curr.execute("PRAGMA foreign_keys = ON")
        for attribute, value in attributes.items():
            curr.execute("INSERT INTO audit VALUES (NULL, ?, ?, ?)",
                          (attribute, value, scan_id))
