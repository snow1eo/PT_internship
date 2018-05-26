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
    os = detect_os()
    snmp_audit()
    ssh_audit_cisco()
    if os != 'unknown':
        ssh_audit_unix()


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
    vendor, version, = sysDescr_data.splitlines()[:2]
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


def ssh_audit_cisco():
    try:
        ssh = get_transport('SSH')
        os_info = '\n'.join(ssh.execute_show('show version').splitlines()[:2])
        users = '\n'.join(s for s in
            ssh.execute_show('show running-config').splitlines()
            if s.startswith('username'))
        # TODO MACs
        set_attributes(dict(
            OS=os_info,
            Users=users))
    except TransportConnectionError:
        return
    


def ssh_audit_unix():
    try:
        ssh = get_transport('SSH')
        set_attributes(dict(Packages='\n'.join('{}: {}'.format(pkg, ver) for 
            pkg, ver in get_packages(ssh).items())))
    except TransportConnectionError:
        return


def set_attributes(attributes):
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


def detect_os():
    try:
        ssh = get_transport('SSH')
        raw_os = ssh.execute_show('uname -a')
        if not raw_os.startswith('Linux'):
            return raw_os.split()[0]
        raw_os = raw_os.lower()
        if 'debian' in raw_os:
            return 'Debian Linux'
        elif 'centos' in raw_os:
            return 'CentOS Linux'
        elif 'ubuntu' in raw_os:
            return 'Ubuntu Linux'
        elif 'arch' in raw_os:
            return 'Arch Linux'
        else:
            return 'Unknown Linux'
    except TransportConnectionError:
        return 'Unknown'
