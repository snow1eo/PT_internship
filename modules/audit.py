import re
import sqlite3
from enum import IntEnum

from modules.database import DB_NAME, get_scan_id, init_scanning
from modules.errors import RemoteHostCommandError, TransportConnectionError, \
    SNMPError, SNMPStatusError
from modules.transports import get_transport


class IfaceStatus(IntEnum):
    UP = 1
    DOWN = 2
    TESTING = 3
    UNKNOWN = 4
    DORMANT = 5
    NOT_PRESENT = 6
    LOWER_LAYER_DOWN = 7


def audit():
    init_scanning()
    snmp_audit()
    ssh_audit()


def snmp_audit():
    sysDescr = '.1.3.6.1.2.1.1.1.0'
    ifNumber = '.1.3.6.1.2.1.2.1.0'
    ifDescr = '.1.3.6.1.2.1.2.2.1.2.{num}'
    ifOperStatus = '.1.3.6.1.2.1.2.2.1.8.{num}'

    ifaces = list()
    try:
        snmp = get_transport('SNMP')
        sysDescr_data = snmp.get_snmpdata(sysDescr)[0]
        iface_number = int(snmp.get_snmpdata(ifNumber)[0])
        for i_num in range(1, iface_number + 1):
            ifaces.append(snmp.get_snmpdata(
                ifDescr.format(num=i_num),
                ifOperStatus.format(num=i_num)))
    except (TransportConnectionError, SNMPError, SNMPStatusError):
        return
    ifaces = tuple(map(lambda x: [x[0], IfaceStatus(int(x[1])).name], ifaces))
    vendor, version, = sysDescr_data.split('\n')[:2]
    attributes = dict(
        vendor=vendor,
        software_version=version,
        interfaces='\n'.join(["Ifnterface: {}, status: {}".format(*iface)
                              for iface in ifaces]))
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
        OS=ssh.execute_show('cat /proc/version'),
        Users=ssh.execute_show('cat /etc/passwd'),
        MACs=ssh.execute_show('ip l'),
        Packages='\n'.join('{}: {}'.format(pkg, ver) for pkg, ver
                           in get_packages(ssh).items()))
    with sqlite3.connect(DB_NAME) as db:
        curr = db.cursor()
        curr.execute("PRAGMA foreign_keys = ON")
        for attribute, value in attributes.items():
            curr.execute("INSERT INTO audit VALUES (NULL, ?, ?, ?, ?)",
                         (attribute, value, 'SSH', get_scan_id()))


def get_packages(ssh):
    try:
        pkgs = re.findall(r'ii\s+(\S+)\s+(\S+)',
                          ssh.execute_show('dpkg -l'))
        return {p[0]: p[1] for p in pkgs}
    except RemoteHostCommandError:
        pass
    try:
        pkgs = re.findall(r'(\S+)-(\S+)',
                          ssh.execute_show('rpm -qa'))
        return {p[0]: p[1] for p in pkgs}
    except RemoteHostCommandError:
        pass
