import wmi
import json
import csv
import sqlite3
temp = ''
temp2 = ''
temp3 = ''
s = ''
vul_list = []
os_list = []
id_list = []
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

def db_add(cursor,table,values):
    cursor.execute("INSERT INTO "+table+" VALUES "+str(values))

def db_show(cursor, table):
    cursor.execute("SELECT ROWID, * FROM "+table)
    for row in cursor:
        print(row)
        
def db_create(cursor):
    table_name = input()
    columns = input()
    command = ('CREATE TABLE IF NOT EXISTS '+table_name+'(id INTEGER PRIMARY KEY, '+columns+')')
    cursor.execute(command)

hosts = ("172.16.22.11","172.16.22.10")
mem_db = sqlite3.connect('example.db')
curr = mem_db.cursor()
def task_1(hosts):
    c = wmi.WMI(computer = hosts[0],
     user = "administrator",
     password = "P@ssw0rd"
     )
    d = wmi.WMI(computer = hosts[1],
     user = "administrator",
     password = "P@ssw0rd"
     )

    data_to_put = {'data_1':{'Index':'','IPAddress':'','MACAddress':''},'data_2':{'Index':'','IPAddress':'','MACAddress':''}}
    

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
    curr.execute("INSERT INTO audit VALUES "+str((1, "Index",  data_to_put['data_1']['Index'])))
    curr.execute("INSERT INTO audit VALUES "+str((2, "IPAddress",  data_to_put['data_1']['IPAddress'])))
    curr.execute("INSERT INTO audit VALUES "+str((3, "MACAddress",  data_to_put['data_1']['MACAddress'])))
    curr.execute("INSERT INTO audit VALUES "+str((4, "Index",  data_to_put['data_2']['Index'])))
    curr.execute("INSERT INTO audit VALUES "+str((5, "IPAddress",  data_to_put['data_2']['IPAddress'])))
    curr.execute("INSERT INTO audit VALUES "+str((6, "MACAddress",  data_to_put['data_2']['MACAddress'])))
    curr.execute("SELECT ROWID, * FROM audit")
    f = open('report.txt', 'w')
    f.write("Task 1:" + '\n')
    for row in curr:
        f.write(str(row) + '\n')
        print(row)
    f.write("Task 2:" + '\n')
    return 0

def task_2():
    hosts = ("172.16.22.11","172.16.22.10")
    c = wmi.WMI(computer = hosts[0],
     user = "administrator",
     password = "P@ssw0rd"
     )
    d = wmi.WMI(computer = hosts[1],
     user = "administrator",
     password = "P@ssw0rd"
     )
    win7KBlist = []
    win2012KBlist = []
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
            else:
                print('ALARM!'+vul_list[i])
                
    del_able = found

    for i in range(len(vul_list)):
        if os_list[i] == '7':
            if vul_list[i] in win7KBlist:
                for it in range(len(found)):
                    if found[it][1] == id_list[i]:
                        del(del_able[it])

    del_able = (list(set(del_able)))

    result = []
    for i in range(len(del_able)):
        for j in range(len(to_bd)):
            if del_able[i][0] == 'Server':
                if del_able[i][1] == to_bd[j].get('Code'):
                    result.append(to_bd[j])
            else:
                if del_able[i][1] == to_bd[j].get('Code'):
                    result.append(to_bd[j])
    for z in range(4):
        curr.execute("INSERT INTO drawback VALUES "+str((z+1, str(to_bd[z]['OS'])+' '+str(to_bd[z]['Code']),  str(to_bd[z]['Title']), str(to_bd[z]['Description']))))
    curr.execute("SELECT ROWID, * FROM drawback")
    f = open('report.txt', 'a')
    for row in curr:
        f.write(str(row) + '\n')
        print(row)
    return 0

def main():
    task_1(hosts)
    task_2()

if __name__ == "__main__":
    main()
