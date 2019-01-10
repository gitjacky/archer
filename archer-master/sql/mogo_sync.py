#!/usr/local/bin/python3.4
#-*-coding: utf-8-*-
import pymongo
from bson.objectid import ObjectId
import os
import json
import time
import re
from .aes_decryptor import Prpcrypt
from datetime import date,datetime
from dateutil import parser
from .models import mongo_config

prpCryptor = Prpcrypt()

cur_tm = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
tm = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
pid = os.getpid()

class SyncSc(object):

    def __init__(self,service_name,code_type,from_env,to_env,url_choice):
        self.service_name = service_name
        self.code_type = code_type
        self.from_env = from_env
        self.to_env = to_env
        self.url_choice = url_choice

        # 接口源环境

    def find_code(self):
        global file_name
        file_name = "nowrite"
        self.db_connects(self.from_env)
        env = 'from_env'
        s_result = self.s_search(env)
        #print(s_result)
        #print("source_list", source_list)
        if source_list:
            return source_list
        else:
            return False


    #接口源环境
    def s_code(self):
        # global file_name
        check_result = self.check_file()
        #print(check_result)
        if check_result:
            self.db_connects(self.from_env)
            env = 'from_env'
            s_result = self.s_search(env)
            #print(s_result)
            if s_result:
                return s_result
            else:
                return False
        else:
            os.remove(file_name)
            return ("inuse")

    #接口目的环境
    def t_code(self):

        if self.to_env and self.service_name:
            self.db_connects(self.to_env)
            env = 'to_env'
            port_es = self.s_search(env)
            if port_es:
                os.remove(file_name)
                return "已存在"
            else:
                print("%s%s%s%s" % ("\n",self.to_env," 不存在!","\n"))

                json_f = open(file_name,'r')
                json_content = json.load(json_f)
                dict_json = json.loads(json_content)
                json_f.close()

                #定时器
                if self.code_type == 1:
                    t_tsstimer = db.tssTimer
                    tss = {}
                    for i in dict_json:
                        if 'tssTimer' in i:
                            print(i['tssTimer'])
                            tss_id = i['tssTimer']['_id']
                            i['tssTimer']['_id'] = ObjectId(tss_id)
                            if 'addTime' in i['tssTimer'] and i['tssTimer']['addTime']:
                                i['tssTimer']['addTime'] = parser.parse(i['tssTimer']['addTime'])
                            else:
                                pass
                            if 'updateTime' in i['tssTimer'] and i['tssTimer']['updateTime']: 
                                i['tssTimer']['updateTime'] = parser.parse(i['tssTimer']['updateTime'])
                            else:
                                pass
                            if 'startTime' in i['tssTimer'] and i['tssTimer']['startTime']: 
                                i['tssTimer']['startTime'] = parser.parse(i['tssTimer']['startTime'])
                            else:
                                pass
                            if 'endTime' in i['tssTimer'] and i['tssTimer']['endTime']: 
                                i['tssTimer']['endTime'] = parser.parse(i['tssTimer']['endTime'])
                            else:
                                pass
                            tss = i['tssTimer']

                    try:
                        if tss:
                            t_tsstimer.insert_one(tss)
                            print("已完成")
                            os.remove(file_name)
                            return "已完成"
                        else:
                            pass
                    except pymongo.errors.DuplicateKeyError as dk:
                        raise dk
                    except Exception as e:
                        raise e
                        os.remove(file_name)
                #MQ队列
                elif  self.code_type == 2:
                    t_mqqueue = db.mQQueue
                    mq = {}
                    for i in dict_json:
                        if 'mQQueue' in i:
                            print(i['mQQueue'])
                            mq_id = i['mQQueue']['_id']
                            i['mQQueue']['_id'] = ObjectId(mq_id)
                            mq = i['mQQueue']

                    try:
                        if mq:
                            t_mqqueue.insert_one(mq)
                            print("已完成")
                            os.remove(file_name)
                            return "已完成"
                        else:
                            pass
                    except pymongo.errors.DuplicateKeyError as dk:
                        raise dk
                    except Exception as e:
                        raise e
                        os.remove(file_name)
                #接口
                else:
                    t_sysinfo = db.sysInfo
                    t_resource = db.resource
                    t_flow = db.flow
                    t_service = db.service
                    
                    resource = {}
                    flow = {}
                    flow2 = {}
                    service = {}

                    for i in dict_json:
                        if 'sysinfo' in i:
                            sysid = i['sysinfo']['_id']
                            sysinfo = i['sysinfo']
                            sys_pro = (sysinfo['hosts'][0]['address']).split('/')[-1]
                            if sys_pro == '':
                                sys_pro = (sysinfo['hosts'][0]['address']).split('/')[-2]
                            else:
                                pass
                            dest_urls = t_sysinfo.find({"hosts.address":{'$regex':sys_pro}})
                               
                            #目的环境可选sysInfo信息存放至sys_dicts
                            sys_dicts = {}
                            i_count = 0
                            for i in dest_urls:
                                i_count  = i_count + 1
                                sys_dicts[i_count] = i


                            #目地环境若存在类似的url
                            sys_urls = []
                            syss = {}
                            if sys_dicts:
                                #print("可选sysInfo: \n\n")
                                for i in sys_dicts:
                                    print("%s) %s" % (str(i),sys_dicts[i]['hosts'][0]['address']))
                                    sys_urls.append(sys_dicts[i]['hosts'][0]['address'])
                                    syss[sys_dicts[i]['_id']] = sys_dicts[i]['hosts'][0]['address']
                                #print("\n")
                                #print("sys_urls",sys_urls)
                                #print("syss", syss)

                                #第一次请求，没有用户返回值
                                if not self.url_choice:
                                    os.remove(file_name)
                                    return sys_urls
                                #第二次请求，有用户返回值
                                else:
                                    my_choice = list(syss.keys())[list(syss.values()).index(self.url_choice)]
                                    n_sysid = my_choice
                            else:
                                #print(("%s%s") % ("提示：目地环境还没有类似sysInfo,请手工先插入对应sysInfo记录后再运行本脚本！",'\n'))
                                os.remove(file_name)
                                return("提示：目地环境还没有类似sysInfo,请手工插入对应sysInfo后再同步！")

                                # exit(0)

                        elif 'resource' in i:
                            n_sysid = ''
                            resource_id = i['resource']['_id']
                            i['resource']['_id'] = ObjectId(resource_id)
                            resource = i['resource']

                        elif 'flow' in i:
                            flow_id = i['flow']['_id']
                            i['flow']['_id'] = ObjectId(flow_id)
                            flow = i['flow']

                        elif 'flow2' in i:
                            flow2_id = i['flow2']['_id']
                            i['flow2']['_id'] = ObjectId(flow2_id)
                            flow2 = i['flow2']

                        elif 'service' in i:
                            service_id = i['service']['_id']
                            i['service']['_id'] = ObjectId(service_id)
                            service = i['service']
                         
                    if resource and n_sysid:
                        resource['sysId'] = str(n_sysid).split('"')[0]
                        #print(resource)
                    else:
                        pass


                    try:
                        if resource:
                            t_resource.insert_one(resource)
                        else:
                            pass
                        if flow:
                            t_flow.insert_one(flow)
                        else:
                            pass
                        if flow2:
                            t_flow.insert_one(flow2)
                        else:
                            pass
                        if service:
                            t_service.insert_one(service)
                        else:
                            pass

                        os.remove(file_name)
                        #print("已完成")
                        return "已完成"

                    except pymongo.errors.DuplicateKeyError as dk:
                        raise dk
                    except Exception as e:
                        raise e

                    os.remove(file_name)

        else:
            print("所提供目的环境有误!")
            os.remove(file_name)

    #编码查询
    def s_search(self, env):
        '''查询mongo接口是否存在,如果不存在就给出提示.'''
        global source_list
        source_list = []

        # 定时器
        if self.code_type == 1:
            mytsstimer = db.tssTimer
            tsstimer_re = mytsstimer.find_one({"code": self.service_name})
            tss_collect = {}
            tss_collect['tssTimer'] = tsstimer_re
            source_list.append(tss_collect)
            print(source_list)

            if not tsstimer_re and env == 'from_env':
                print("定时器不存在！\n")
                return "notexist"

            elif not tsstimer_re and env == 'to_env':
                pass
            else:
                # 将源环境接口数据写入json文件
                if env == 'from_env' and file_name != "nowrite":
                    json_f = open(file_name, 'w', encoding='utf8')
                    json.dump(JSONEncoder().encode(source_list), json_f)
                    json_f.close()
                    return True
                else:
                    return True
        # MQ
        elif self.code_type == 2:
            mymq = db.mQQueue
            mq_re = mymq.find_one({"name": self.service_name})
            mq_collect = {}
            mq_collect['mQQueue'] = mq_re
            source_list.append(mq_collect)
            if not mq_re and env == 'from_env':
                print("MQ不存在！\n")
                return "notexist"

            elif not mq_re and env == 'to_env':
                pass
            else:
                # 将源环境接口数据写入json文件
                if env == 'from_env' and file_name != "nowrite":
                    json_f = open(file_name, 'w', encoding='utf8')
                    json.dump(JSONEncoder().encode(source_list), json_f)
                    json_f.close()
                    return True
                else:
                    return True
        # 接口
        else:
            myservice = db.service
            service_re = myservice.find_one({"serviceCode": self.service_name})
            if not service_re and env == 'from_env':
                print("notexist")
                return "notexist"
            elif not service_re and env == 'to_env':
                return False
            else:
                # 源环境service信息添加到嵌套列表
                collect = {}
                collect['service'] = service_re
                source_list.append(collect)

            dic = {}
            dic = service_re
            myflow = db.flow
            flow_id = dic["flowId"]
            flow_re = myflow.find_one({"_id": ObjectId(flow_id)})
            f = flow_re["componentQueue"]
            f_subid = dict(f[0])["componentSettings"]
            global sysid

            # 源环境flow信息添加到嵌套列表
            collect = {}
            collect['flow'] = flow_re
            source_list.append(collect)

            # 若第一条flow记录里带resourceId,则为同步接口类型
            if 'resourceId' in f_subid:
                # resource
                # print("[接口类型]：同步接口\n")
                rs_id = f_subid["resourceId"]
                myresource = db.resource
                resource_re = myresource.find_one({"_id": ObjectId(rs_id)})
                c1 = resource_re

                # 源环境resource信息添加到嵌套列表
                collect = {}
                collect['resource'] = resource_re
                source_list.append(collect)

                # 查询同步接口的sysInfo
                sysid = c1["sysId"]
                mysys = db.sysInfo
                sys_info = mysys.find_one({"_id": ObjectId(sysid)})
                #print(sys_info['hosts'])

                # 源环境sysInfo信息添加到嵌套列表
                collect = {}
                collect['sysinfo'] = sys_info
                source_list.append(collect)
                global s_info
                s_info = sys_info['hosts']

            # 若第一条flow里有flowId,则该接口属于异步接口类型
            elif 'flowId' in f_subid:
                # 异步flow
                # print("[接口类型]：异步接口\n")

                # 查找第二条flow2记录
                myflow1 = db.flow
                fw_id = f_subid["flowId"]
                flow_re2 = myflow1.find_one({"_id": ObjectId(fw_id)})

                # 源环境异步flow2信息添加到嵌套列表
                collect = {}
                collect['flow2'] = flow_re2
                source_list.append(collect)

                # 查找异步resource记录
                myresource = db.resource
                g = flow_re2["componentQueue"]
                rs1_id = dict(g[0])["componentSettings"]["resourceId"]
                resource_re = myresource.find_one({"_id": ObjectId(rs1_id)})
                sysid = resource_re["sysId"]

                # 源环境异步resource信息添加到嵌套列表
                collect = {}
                collect['resource'] = resource_re
                source_list.append(collect)

                # 查找sysInfo记录
                mysys = db.sysInfo
                sys_info = mysys.find_one({"_id": ObjectId(sysid)})
                #print(sys_info['hosts'])

                # 源环境异步sysInfo信息添加到嵌套列表
                collect = {}
                collect['sysinfo'] = sys_info
                source_list.append(collect)
                global s_info
                s_info = sys_info['hosts']

            # 否则就是只有两条记录的生成器接口
            else:
                print("生成器信息：由flow中queue到mQQueue中查到name为queue的队列，同步队列与生成器\n")

            # 将源环境接口数据写入json文件
            if env == 'from_env' and file_name != "nowrite":
                json_f = open(file_name, 'w', encoding='utf8')
                json.dump(JSONEncoder().encode(source_list), json_f)
                json_f.close()

            else:
                pass

            return s_info

    #不同环境连接信息
    def db_connects(self,env_name):
        mgconfig = mongo_config.objects.get(db_name=env_name)
        mogohost = mgconfig.mongo_host
        mogoport = mgconfig.mongo_port
        mogouser = mgconfig.mongo_user
        mogopass = prpCryptor.decrypt(mgconfig.mongo_password)

        try:
            db = []
            conn = None
            conn = pymongo.MongoClient(host=mogohost, port=int(mogoport))
            db = conn.gesb
            db.authenticate(mogouser, mogopass)
            if env_name == self.from_env:
                if self.code_type == 1:
                    code_tp = "定时器"
                elif self.code_type == 2:
                    code_tp = "MQ"
                else:
                    code_tp = "接口"
                print("\n%s %s 从 %s 同步到 %s \n" % (code_tp,self.service_name, self.from_env.upper(), self.to_env.upper()))
            else:
                pass
            #print("%s %s %s" % (30 * "*", str(env_name).upper(), 30 * "*"))
            global db
            return db
        except Exception as e:
            print(str(e))
            return str(e)

    def check_file(self):
        # 若已经有人在运行本脚本，则提示并退出，否则就运行
        global file_name
        file_name = '/tmp/' + str(pid) + '.json'
        if os.path.exists(file_name):
            print(("%s%s%s") % ('\n', "正在同步!", '\n'))
            return False
        else:
            return True

#处理objectid的hook
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime):  
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(o, date):  
            return o.strftime('%Y-%m-%d')  
        else:
            return json.JSONEncoder.default(self, o)
