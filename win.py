import wmi
import json
import csv
temp = ''
temp2 = ''
temp3 = ''
s = ''
vul_list = []
os_list = []
id_list = []

#s[4] - коды уязвимостей
#s[1] - title
#s[2] - desc

to_bd = []
with open('CVE_ID-KB.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        temp = row[0].split(';')
        if len(temp) == 2:
            vul_list.append(temp[0])
        if len(row) != 1:
            temp2 = row[1].split(';')
            if len(temp2) == 2:
                os_list.append(temp2[0])
                id_list.append(temp2[1])
            else:
                os_list.append(temp2[0])
                temp3 = row[3].split(';')
                id_list.append(temp3[1])

with open('CVE_ID-OSversion.csv', 'r') as csvfile:
    read = csv.reader(csvfile)
    for row in read:
        s = row[0].split(';')
        to_bd.append(dict(OS=s[0],Title=s[1],Description=s[2],Code=s[4]))

#print(to_bd[0])

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

wql = "SELECT IPAddress, MACAddress FROM Win32_NetworkAdapterConfiguration where ipenabled = true"
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

found = []

for i in range(len(vul_list)):
    if os_list[i] == '7':
        if vul_list[i] not in win7KBlist:
            found.append((os_list[i],id_list[i]))
    else:
        if vul_list[i] not in win2012KBlist:
            found.append((os_list[i],id_list[i]))

found = (list(set(found)))
for i in range(len(found)):
    for j in range(len(to_bd)):
        if found[i][0] == 'Server':
            if found[i][1] == to_bd[j].get('Code'):
                print(to_bd[j].get('Code')+' '+to_bd[j].get('OS'))
        else:
            if found[i][1] == to_bd[j].get('Code'):
                print(to_bd[j].get('Code')+' '+to_bd[j].get('OS'))
                
