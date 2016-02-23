#!/usr/bin/env python
#coding:utf8
import time,os
import urllib
import urllib2
import cookielib
import MySQLdb
import smtplib
from email.mime.text import MIMEText
'''
screens = [
    u'IDC防火墙',
    #u'Oracle服务器',
    #u'Mysql服务器',
    #u'www.ippjr.com(帝友)',
    #u'生产系统服务器负载',
    #u'生产系统服务器网络',
    #u'生产系统服务器内存',
    #u'生产系统服务器磁盘使用量',
    #u'生产系统服务器磁盘IO',
]
'''
screensids = ['27','46','47','29','41','42','43','44','45']
save_graph_path = "/data/zabbix/web/zabbix/reports/%s"%time.strftime("%Y-%m-%d")
if not os.path.exists(save_graph_path):
    os.makedirs(save_graph_path)
zabbix_host = "zabbix.ippjr-idc.com"
username = "admin"
password = " TdQ3h62E"
width = 500
height = 100
#period = 86400   #1天
period = 604800  #7天
#dbhost = "10.10.10.25"
dbhost = "127.0.0.1"
dbport = 3306
dbuser = "tanzhixu"
dbpasswd = "tanzhixu"
dbname = "zabbix"

'''
to_list = [""]
smtp_server = ""
mail_user = ''
mail_pass = ''
domain = "163.com"
'''

def mysql_query(command):
    try:
        conn = MySQLdb.connect(host=dbhost,user=dbuser,passwd=dbpasswd,db=dbname,port=int(dbport))
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

def write_file(filename,data):
    with open(filename, 'wb') as f:
        f.write(data)

def get_graph(zabbix_host,username,password,screen,width,height,period,save_graph_path):
    #global html
    #html = ''
    html_head = '''
    <!DOCTYPE html>
    <html>
    <head lang="en">
    <meta charset="UTF-8">
    <title>zabbix report</title>
    </head>
    <body>
    '''
    html_body = '''
    </body>
    </html>
    '''

    for screenid in screen:
        graphid_list = []
        html = ''
        for c in mysql_query("select resourceid,y from screens_items where screenid='%s'" % int(screenid)):
            graphid_list.append(int(c[0]))
        for graphid in graphid_list:
            login_opt = urllib.urlencode({
            "name": username,
            "password": password,
            "autologin": 1,
            "enter": "Sign in"})
            get_graph_opt = urllib.urlencode({
            "graphid": graphid,
            "screenid": screenid,
            "width": width,
            "height": height,
            "period": period})
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            login_url = r"http://%s/index.php" % zabbix_host
            save_graph_url = r"http://%s/chart2.php" % zabbix_host
            opener.open(login_url,login_opt).read()
            data = opener.open(save_graph_url,get_graph_opt).read()
            filename = "%s/%s.%s.png"%(save_graph_path,screenid,graphid)
            html += '<img width="600" height="250" src="http://%s/%s/%s/%s.%s.png">'%(zabbix_host,save_graph_path.split("/")[len(save_graph_path.split("/"))-2],save_graph_path.split("/")[len(save_graph_path.split("/"))-1],screenid,graphid)
            write_file(filename=filename,data=data)
        filename = "%s/index-%s.html" % (save_graph_path,screenid)
        htmltmp = html_head + html + html_body
        write_file(filename=filename,data=htmltmp)

def send_mail(username,password,smtp_server,to_list,sub,content):
    me = "zabbix report"+"<"+username+"@"+domain +">"
    msg = MIMEText(content,_subtype="html",_charset="utf8")
    msg["Subject"] = sub
    msg["From"] = me
    msg["To"] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(smtp_server)
        server.login(username,password)
        server.sendmail(me,to_list,msg.as_string())
        server.close()
        print "send mail Ok!"
    except Exception, e:
        print e

if __name__ == '__main__':
    get_graph(zabbix_host,username,password,screensids,width,height,period,save_graph_path)
    #send_mail(mail_user,mail_pass,smtp_server,to_list,"zabbix report email",html)
    #print html
