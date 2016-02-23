#!/usr/bin/env python
#coding:utf8
import json
import urllib2
class zabbixtools:
    def __init__(self):
        self.url = "http://zabbix.ippjr-inc.com/api_jsonrpc.php"
        self.header = {"Content-Type": "application/json"}
        self.authID = self.user_login()
    def user_login(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "user.login",
                    "params": {
                        "user": "zabbix_readonly",
                        "password": "zabbix_readonly"
                        },
                    "id": 0
                    })
        request = urllib2.Request(self.url,data)
        for key in self.header:
            request.add_header(key,self.header[key])
        result = urllib2.urlopen(request)
        response = json.loads(result.read())
        result.close()
        print response
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
    def hostgroup_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostgroup.get",
                    "params": {
                        "output": "extend",
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
        if 'result' in res.keys():
            res = res['result']
            if (res !=0) or (len(res) != 0):
                print "Number Of Template: %d" % len(res)
                for group in res:
                    print"\t","Template_id:",group['groupid'],"\t","Template_Name:",group['name'].encode('GBK')
        else:
            print "Get Template Error,please check !"


    def host_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output": "extend",
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
        if 'result' in res.keys():
            res = res['result']
            if (res !=0) or (len(res) != 0):
                print "Number Of host: %d" % len(res)
                for host in res:
                    #print"\t","host_id:",host['hostid'],"\t","host_name:",host['name'].encode('utf-8')
                    print host['name'].encode('utf-8'),"\t",host['host'],'\t',host['hostid']
                    #print host['name'],'\t',host['status']
        else:
            print "Get Template Error,please check !"


    def template_get(self):
        data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "template.get",
                    "params": {
                        "output": "extend",
                        },
                    "auth": self.authID,
                    "id": 1,
                    })
        res = self.get_data(data)
        if 'result' in res.keys():
            res = res['result']
            print res[0]
            for k in res:
                print k['name'],'\t',k['templateid']
    def change_template(self,n):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.update",
                "params": {
                    "hostid": n,
                    "templates_clear": [{"templateid":"10620"},{"templateid":"12112"}],
                    "templates":[{"templateid":"12142"},{"templateid":"12112"}],
                    "status":0
                    },
                "auth": self.authID,
                "id": 1
                })
        res = self.get_data(data)
        print res
    def get_history(self,itemid):
        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "history.get",
                "params": {
                    "output":"extend",
                    "history":0,
                    "itemids":itemid,
                    "limit":2
                    },
                "auth": self.authID,
                "id": 1
                })
        res = self.get_data(data)
        print res


    def create_item(self,itemname,hostid,delay):
        itemmessage = {
            "memavailable":{"itemname":"Available memory","itemkey":"vm.memory.size[available]"},
            "cpuavailable":{"itemname":"Available cpu","itemkey":"system.cpu.util[,idle]"},
            }
        #itemkey = '{%s:%s.last(0)}<%sM' % (ip,itemmessage[name]["triggerkey"],threshold)
        data = json.dumps(
            {
                "jsonrpc":"2.0",
                "method":"item.create",
                "params":{
                    "name":itemmessage[itemname]["itemname"],
                    "key_":itemmessage[itemname]["itemkey"],
                    "hostid":hostid,
                    "type":0,
                    "value_type":0,
                    "delay":delay
                },
             "auth":self.authID,
             "id":1
            }
        )
        item = self.get_data(data)
        print item
        itemid = item['result']['itemids'][0]
        return itemid

    def get_hostgroup(self):
        data = json.dumps(
            {
                "jsonrpc":"2.0",
                "method":"hostgroup.get",
                "params":{
                    "output":"extend"
                },
             "auth":self.authID,
             "id":1
            }
        )

        hostgroup = self.get_data(data)
        hostgrouplist = []
        for group in hostgroup['result']:
            hgl = {}
            hgl['hostgroupid'] = group['groupid']
            hgl['hostgroupname'] = group['name']
            hostgrouplist.append(hgl)
        print  hostgrouplist

    def update_usergroup(self,usrgrpid,hostgrpid,permission=2):
        data = json.dumps(
            {
                "jsonrpc":"2.0",
                "method":"usergroup.update",
                "params":{
                    "usrgrpid":usrgrpid,
                    "rights":{
                      "permission":permission,
                      "id":hostgrpid
                    },
                },
             "auth":self.authID,
             "id":1
            }
        )
        print  self.get_data(data)

    def create_user(self,username,usergroupid):
        data = json.dumps(
            {
                "jsonrpc":"2.0",
                "method":"user.create",
                "params":{
                    "alias":username,
                    "passwd":"123456",
                    "usrgrps":[{
                        "usrgrpid":usergroupid
                    }]
                },
                "auth":self.authID,
                "id":1
            })
        print self.get_data(data)

    def create_host(self,hostip,type,port,groupid):
        data = json.dumps(
            {
                "jsonrpc":"2.0",
                "method":"host.create",
                "params":{
                    "host":hostip,
                    "interfaces":[{
                        "type":type,
                        "main":1,
                        "useip":1,
                        "ip":hostip,
                        "dns":"",
                        "port":port,
                    }],
                "groups":[{
                        "groupid":groupid
                    }]
                },
             "auth":self.authID,
             "id":1
            }
        )
        print self.get_data(data)

    def get_usergroup(self):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "usergroup.get",
            "params": {
                "output": "extend",
            },
            "auth":self.authID,
            "id": 1
            }
        )
        print self.get_data(data)
    def get_user(self):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "user.get",
            "params": {
                "output": "extend",
            },
            "auth":self.authID,
            "id": 1
            }
        )
        print self.get_data(data)

    def get_mediatype(self):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "mediatype.get",
            "params": {
                "output": "extend",
            },
            "auth":self.authID,
            "id": 1
            }
        )
        print self.get_data(data)
    def get_item(self,hostids):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": "extend",
                "hostids":hostids
            },
            "auth":self.authID,
            "id": 1
            }
        )
        return  self.get_data(data)['result']

    def get_ddlrule(self,hostids):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "discoveryrule.get",
            "params": {
                "output": "extend",
                "hostids":hostids
            },
            "auth":self.authID,
            "id": 1
            }
        )
        return  self.get_data(data)['result']

    def delete_ddlrule(self,ddlruleids):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "discoveryrule.delete",
            "params": [ ddlruleids ],
            "auth":self.authID,
            "id": 1
            }
        )
        return  self.get_data(data)['result']

    def get_trigger(self,hostid):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "hostids":hostid,
                "output":"extend",
            },
            "auth":self.authID,
            "id": 1
            }
        )
        print  self.get_data(data)['result']

    def get_item(self,hostid):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output":"extend",
                "hostids":hostid,
            },
            "auth":self.authID,
            "id": 1
            }
        )
        return  self.get_data(data)['result']

    def get_itemprototype(self,hostids):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "itemprototype.get",
            "params": {
                "output":"extend",
                "hostids":hostids,
            },
            "auth":self.authID,
            "id": 1
            }
        )
        return  self.get_data(data)['result']

    def update_trigger(self,triggerid,expression):
        data = json.dumps(
            {
            "jsonrpc": "2.0",
            "method": "trigger.update",
            "params": {
                "triggerid":triggerid,
                "expression":expression,
            },
            "auth":self.authID,
            "id": 1
            }
        )
        print  self.get_data(data)['result']

    def get_action(self,hostids):
        data = json.dumps(
            {
                "jsonrpc":"2.0",
                "method":"action.get",
                "params":{
                    "output":"extend",
                    "hostids":hostids,
                    "filter":{"eventsource":0}
                },
                "auth":self.authID,
                "id":1
            }
        )
        print self.get_data(data)['result']

    def create_action(self,hostid,userid,mediatypeid,):
        data = json.dumps(
        {
        "jsonrpc": "2.0",
        "method": "action.create",
        "params": {
                "name":"sdfssdfsdfdf",
                "eventsource": 0,
                "status": 0,
                "esc_period": 120,
                "def_shortdata": "{TRIGGER.NAME}: {TRIGGER.STATUS}",
                "def_longdata": "{TRIGGER.NAME}: {TRIGGER.STATUS}\r\nLast value: {ITEM.LASTVALUE}\r\n\r\n{TRIGGER.URL}",
                "filter": {
                    "evaltype": 0,
                    "conditions": [
                        {
                            "conditiontype": 1,
                            "operator": 0,
                            "value": hostid
                        },
                        {
                           "conditiontype": 5,
                            "operator": 0,
                            "value": "1"
                        }
                    ]
                },
                "operations": [
                    {
                        "operationtype": 0,
                        "esc_period": 0,
                        "esc_step_from": 1,
                       "esc_step_to": 1,
                        "evaltype": 0,
                        "opmessage_usr": [
                                    {
                                        "userid": userid
                                    }
                                ],
                        "opmessage": {
                           "default_msg": 1,
                            "mediatypeid": mediatypeid
                       }
                    },
                ]
           },
            "auth": self.authID,
           "id": 1
            }

        )
        print self.get_data(data)

def main():
    test = zabbixtools()
    #test.host_get()
    #test.get_action(hostids='10272')
    #test.create_item(itemname='memavailable',hostid='10241',delay='30')
    #test.get_hostgroup()
    #test.update_usergroup(usrgrpid='26',hostgrpid='8',permission=2)
    #test.create_user(username="tanzhixu",usergroupid='34')
    #test.create_host(hostip="192.168.0.3",type='2',port='161',groupid='8')
    #test.get_history(itemid='26588')
    #test.get_item(hostid='10278')
    #test.get_trigger(hostid='10270')
    #test.template_get()
    #for i in range(11970,11969):
    #    test.change_template(i)strategy
    #test.change_template()
    #test.get_usergroup()
    #test.get_user()
    #test.get_mediatype()

    #ddlrulemes = test.get_ddlrule(hostids="10257")
    #print ddlrulemes

    #deleteddl = test.delete_ddlrule(ddlruleids='26049')
    #print deleteddl



    itemmess = test.get_item(hostid="10084")

    for i in range(len(itemmess)):
        print itemmess[i]['hostid'],itemmess[i]['itemid'],itemmess[i]['name'],itemmess[i]['lastvalue']
    #expression = "{tanzhixu_1482810754194210816_192.168.1.3:xmonitor[1482810754194210816,cpu].count(#3,100,\"gt\")}>6"
    #test.update_trigger(triggerid='14997',expression=expression)
    #test.create_action(hostid="10272",userid="19",mediatypeid="1")

if __name__ == "__main__":
    main()