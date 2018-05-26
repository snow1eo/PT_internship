import wmi
import json
import csv
temp = ''
vul_list = []
with open('CVE_ID-KB.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
       # print(" ".join(row),'+')
       temp = row[0].split(';')
       if len(temp) == 2:
           vul_list.append(temp[0])
       


hosts = ("172.16.22.11","172.16.22.10")
c = wmi.WMI(computer = hosts[0],
 user = "administrator",
 password = "P@ssw0rd"
 )
d = wmi.WMI(computer = hosts[1],
 user = "administrator",
 password = "P@ssw0rd"
 )

data_to_put = {'data_1':{'Index':'','IPAddress':'','MACAddress':''},'data_2':{'Index':'','IPAddress':'','MACAddress':''}}
win7KBlist = []
win2012KBlist = []

print(vul_list)

'''wql = "SELECT IPAddress, MACAddress FROM Win32_NetworkAdapterConfiguration where ipenabled = true"
for elem in c.query(wql):
    data_to_put['data_1']['Index'] = elem.Index
    data_to_put['data_1']['IPAddress'] = str(elem.IPAddress).replace("('",'').replace("',)",'')
    data_to_put['data_1']['MACAddress'] = elem.MACAddress

wql = "SELECT IPAddress, MACAddress FROM Win32_NetworkAdapterConfiguration where ipenabled = true"
for elem in d.query(wql):
    data_to_put['data_2']['Index'] = elem.Index
    data_to_put['data_2']['IPAddress'] = str(elem.IPAddress).replace("('",'').replace("',)",'')
    data_to_put['data_2']['MACAddress'] = elem.MACAddress
    with open('NetConf.json', 'w') as outfile:
        json.dump(data_to_put, outfile)


wql = "SELECT HotFixID FROM Win32_QuickFixEngineering"
for hotfix in c.query(wql):
    win7KBlist.append(hotfix.hotfixid)

for hotfix in d.query(wql):
    win2012KBlist.append(hotfix.hotfixid)
print(win7KBlist)
print(win2012KBlist)'''
