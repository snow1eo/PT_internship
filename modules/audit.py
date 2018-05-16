import sqlite3
from base64 import b64encode

from modules.database import DB_NAME, get_scan_id
from modules.errors import SNMPError, SNMPStatusError, TransportConnectionError
from modules.transports import get_transport


def audit():
    snmp_audit()
    ssh_audit()

def snmp_audit():
    sysDescr = '.1.3.6.1.2.1.1.1.0'
    try:
        snmp = get_transport('SNMP')
        sysDescr_data = snmp.get_snmpdata(sysDescr)[sysDescr]
    except SNMPError:
        return
    except SNMPStatusError:
        return
    # TODO some parsing
    # Как это распарсить, если вывод имеет различный формат?
    # Как вытянуть интерфейсы?
    attributes = dict(
        vendor=b64encode('somevendor'.encode()),
        platform=b64encode('someplatform'.encode()),
        software_version=b64encode('v2'.encode()))
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        for attribute, value in attributes.items():
            curr.execute("INSERT INTO audit VALUES (NULL, ?, ?, ?, ?)",
                          (attribute, value, 'SNMP', get_scan_id()))


def ssh_audit():
    try:
        ssh = get_transport('SSH')
    except TransportConnectionError:
        return
    # Как что-то ещё определить?
    attributes = dict(
        OS=ssh.execute_show_b64('cat /proc/version'),
        Users=ssh.execute_show_b64('cat /etc/passwd'),
        MACs=ssh.execute_show_b64('ip l'))  # это те MAC, или как-то по-другому нужно смотреть?
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        for attribute, value in attributes.items():
            curr.execute("INSERT INTO audit VALUES (NULL, ?, ?, ?, ?)",
                          (attribute, value, 'SSH', get_scan_id()))
