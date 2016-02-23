#!/usr/bin/env python
#coding:utf8
import MySQLdb
import time
import datetime
import xlsxwriter
import json
import urllib2
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

mysqlhost = '10.10.10.25'
mysqlport = '3306'
mysqluser = 'tanzhixu'
mysqlpasswd = 'tanzhixu'
mysqldb = 'zabbix'

class zabbixtools:
    def __init__(self):
        self.url = "http://zabbix.ippjr-idc.com/api_jsonrpc.php"
        self.header = {"Content-Type": "application/json"}
        self.authID = self.user_login()
    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": "admin",
                        "password": "TdQ3h62E"
                        },
                    "id": 0
                    })
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        authID = response['result']
        return authID
    def get_data(self,data):
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        return response

    def get_event(self,time_from,time_till,groupids):
        data = json.dumps(
            {
                "jsonrpc":"2.0",
                "method":"event.get",
                "params":{
                    "output":"extend",
                    "groupids":groupids,
                    "time_from": time_from,
                    "time_till": time_till,
                    "sortfield": ["clock"],
                    "sortorder": "ASC"
                },
                "auth":self.authID,
                "id":1
            }
        )
        return self.get_data(data)['result']

def mysql_ddl(command):
    try:
        conn = MySQLdb.connect(host=mysqlhost,user=mysqluser,passwd=mysqlpasswd,db=mysqldb,port=int(mysqlport),charset="utf8")
        cur = conn.cursor()
        cur.execute(command)
        message = cur.fetchall()
        cur.close()
        conn.close()
        return message
    except MySQLdb.Error,e:
        mysqlerror = "Mysql Error %d: %s" % (e.args[0],e.args[1])
        message = {"status":"0","message":mysqlerror}
        return message

def top_100_trigger(time):
    top_100_sql = "SELECT e.objectid,count(distinct e.eventid) AS cnt_event \
            FROM triggers t,events e WHERE t.triggerid=e.objectid AND e.source=0 \
            AND e.object=0 AND e.clock>%s AND t.flags IN ('0','4') \
            GROUP BY e.objectid ORDER BY cnt_event desc" % time
    return mysql_ddl(top_100_sql)

def show_description(triggerid):
    sql = "select description,priority from triggers where triggerid=%s" % triggerid
    return mysql_ddl(sql)

def show_itemid(triggerid):
    sql = "select itemid from functions where triggerid=%s" % triggerid
    return mysql_ddl(sql)

def show_hostid(itemid):
    sql = "select hostid from items where itemid=%s" % itemid
    return mysql_ddl(sql)

def show_name(hostid):
    sql = "select name,host from hosts where hostid=%s" % hostid
    return mysql_ddl(sql)

def get_time_stamp(days=7):
    dayago = (datetime.datetime.now() - datetime.timedelta(days=days))
    timestamp = int(time.mktime(dayago.timetuple()))
    return timestamp

def get_time():
    now = datetime.datetime.now()
    day = now.strftime("%Y-%m-%d")
    return day

def strtotime(s):
    s = float(str(s)[0:10])
    x = time.localtime(s)
    return time.strftime('%Y-%m-%d %H:%M:%S',x)

def write_xlsx(dir,title,chartname,data,c=False):
    chartdir = dir + chartname
    workbook = xlsxwriter.Workbook(chartdir)
    worksheet = workbook.add_worksheet()
    worksheet.set_column('A:A', 40)
    worksheet.set_column('B:B', 50)
    if c:
        worksheet.set_column('C:C', 50)
    format=workbook.add_format()
    format.set_border(1)
    format_title=workbook.add_format()
    format_title.set_border(1)
    format_title.set_bg_color('#cccccc')
    format_title.set_align('center')
    format_title.set_bold()
    worksheet.write_row('A1',title,format_title)
    for i in range(len(data)):
        row =  'A' + str(int(i)+2)
        worksheet.write_row(row, data[i],format)
    workbook.close()

def get_data():
    triggerid = []
    number = []
    description = []
    itemid = []
    hostid = []
    name = []
    hostip = []
    prioritytemp = []
    priority = {'0':u'未分类','1':u'咨询','2':u'警告','3':u'一般严重','4':u'严重','5':u'灾难'}
    top_100_sql_rst = top_100_trigger(time=get_time_stamp())
    for k,v in top_100_sql_rst:
        triggerid.append(k)
        number.append(v)
    for i in triggerid:
        rst1 = show_description(triggerid=i)
        description.append(rst1[0][0])
        prioritytemp.append(rst1[0][1])
        rst2 = show_itemid(triggerid=i)
        itemid.append(rst2[0][0])
    for i in itemid:
        rst = show_hostid(itemid=i)
        hostid.append(rst[0][0])
    for i in hostid:
        rst = show_name(hostid=i)
        name.append(rst[0][0])
        hostip.append(rst[0][1])
    for i in range(len(description)):
        if "{HOSTNAME}" in description[i]:
            description[i] = description[i].replace("{HOSTNAME}",hostip[i])
        if "{HOST.NAME}" in description[i]:
            description[i] = description[i].replace("{HOST.NAME}",hostip[i])
    data = []
    for i in range(len(name)):
        if str(prioritytemp[i]) in '2345':
            data.append([name[i],description[i],priority[str(prioritytemp[i])],number[i]])
    return data

def get_event_data():
    zabbixapi = zabbixtools()
    data = []
    group_info = {
            "AppCan Product Servers": 25,
            "JAVA Product Servers": 12,
            "Mysql Servers" :23,
            "Network Device": 10,
            "Oracle Servers": 14,
            u"数据仓库": 32,
            "PHP Product Servers" : 26,
            "Redis Servers" : 28
            }
    for k,v in group_info.items():
        event_rst = zabbixapi.get_event(time_from=get_time_stamp(days=7),time_till=str(time.time())[:10],groupids=v)
        time_list = []
        hostip = []
        description = []
        triggerid = []
        itemid = []
        hostid = []
        name = []
        for i in range(len(event_rst)):
            time_list.append(strtotime(event_rst[i]['clock']))
            triggerid.append(event_rst[i]['objectid'])
        time_list = list(set(time_list))
        for i in triggerid:
            rst1 = show_description(triggerid=i)
            description.append(rst1[0][0])
            rst2 = show_itemid(triggerid=i)
            itemid.append(rst2[0][0])
        for i in itemid:
            rst = show_hostid(itemid=i)
            hostid.append(rst[0][0])
        for i in hostid:
            rst = show_name(hostid=i)
            name.append(rst[0][0])
            hostip.append(rst[0][1])
        for i in range(len(description)):
            if "{HOSTNAME}" in description[i]:
                description[i] = description[i].replace("{HOSTNAME}",hostip[i])
            if "{HOST.NAME}" in description[i]:
                description[i] = description[i].replace("{HOST.NAME}",hostip[i])
        for i in range(len(time_list)):
            data.append([time_list[i],name[i],description[i]])
    return data

def write_file(filename,data):
    with open(filename, 'wb') as f:
        f.write(data)

def write_to_html(table_name,save_file_path,title,data):
    html_header = '''
    <!DOCTYPE html>
    <html>
    <head lang="en">
    <meta charset="UTF-8">
    <title>zabbix report</title>
    </head>
    <body>
    <center>
    '''
    html_footer = '''
    </body>
    </html>
    '''
    html_body = '''
    <p>%s</p>
    <table width="1000" border="1" bordercolor="black" cellspacing="0">
    <tr>
    '''  % table_name
    for i in range(len(title)):
        th = '''<th>%s</th>''' % title[i]
        html_body += th
    html_body += '''</tr>'''
    for i in data:
        td = ''
        for j in i:
            td += '''<td>%s</td>''' % j
        html_body += '<tr>' + td + '</tr>'
    html_all = html_header + html_body + html_footer
    write_file(save_file_path,html_all)

def main():
    #save_file_path = "/Users/zhitan/Desktop/zabbix/%s/" % time.strftime("%Y-%m-%d")
    save_file_path = "/tmp/"
    if not os.path.exists(save_file_path):
        os.makedirs(save_file_path)
    top_title = [u'主机',u'告警内容',u'严重性',u'告警条数']
    top_chartname = 'top_alert_' + get_time() + ".html"
    event_title = [u'时间',u'主机',u'描述']
    event_chartname = 'week_alert_' + get_time() + ".html"
    #write_xlsx(save_file_path,event_title,event_chartname,get_event_data(),True)
    #write_xlsx(save_file_path,top_title,top_chartname,get_data())
    top_file_dir = save_file_path + top_chartname
    event_file_dir = save_file_path + event_chartname
    write_to_html(u'百大告警事件',top_file_dir,top_title,get_data())
    write_to_html(u'一周告警事件',event_file_dir,event_title,get_event_data())


if __name__ == '__main__':
    main()