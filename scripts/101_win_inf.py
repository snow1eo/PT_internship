
import sys
import traceback

from modules.errors import TransportConnectionError
from modules.statuses import Status
from modules.transports import get_transport

def main():
    wmi = get_transport('WMI',host = '172.16.22.11')
    data_to_put = {'Index':'','IPAddress':'','MACAddress':''}
    wql = "SELECT IPAddress, MACAddress FROM Win32_NetworkAdapterConfiguration where ipenabled = true"
    for elem in wmi.query(wql):
        data_to_put['data_1']['Index'] = elem.Index
        data_to_put['data_1']['IPAddress'] = str(elem.IPAddress).replace("('",'').replace("',)",'')
        data_to_put['data_1']['MACAddress'] = elem.MACAddress 
    return Status.COMPLIANT, data_to_put
