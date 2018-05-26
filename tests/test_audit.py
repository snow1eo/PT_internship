import sqlite3

from modules.audit import audit, ssh_audit_cisco, ssh_audit_unix, snmp_audit
from modules.database import DB_NAME, get_scan_id, init_scanning


def setup_function():
    init_scanning()


def test_audit(run_docker):
    audit()


def test_ssh_audit_pass(run_docker, create_new_database):
    required_attributes = {'OS', 'Users', 'Packages'}
    ssh_audit_cisco()
    ssh_audit_unix()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        attributes = curr.execute("""SELECT attribute FROM audit
                                     WHERE scan_id = ? AND protocol = ?""",
                                  (get_scan_id(), 'SSH')).fetchall()
    attributes = list(map(list, attributes))  # Converting a list
    attributes = set(sum(attributes, []))  # to a linear set
    assert attributes == required_attributes


def test_ssh_audit_no_ssh(no_ssh_connections, create_new_database):
    ssh_audit_cisco()
    ssh_audit_unix()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        assert not curr.execute("""SELECT attribute FROM audit
                                   WHERE scan_id = ? AND protocol = ?""",
                                (get_scan_id(), 'SSH')).fetchall()


def test_snmp_audit_pass(run_docker, create_new_database):
    required_attributes = {'vendor', 'software_version', 'interfaces'}
    snmp_audit()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        attributes = curr.execute("""SELECT attribute FROM audit
                                     WHERE scan_id = ? AND protocol = ?""",
                                  (get_scan_id(), 'SNMP')).fetchall()
    attributes = list(map(list, attributes))  # Converting a list
    attributes = set(sum(attributes, []))  # to a linear set
    assert attributes == required_attributes


def test_snmp_audit_no_snmp(no_snmp_connections, create_new_database):
    snmp_audit()
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        assert not curr.execute("""SELECT attribute FROM audit
                                   WHERE scan_id = ? AND protocol = ?""",
                                (get_scan_id(), 'SNMP')).fetchall()
