# -*- coding: UTF-8 -*-
import re
import pymysql
from django.conf import settings

regex = r'\s*use\s+\`\w+\-*\w*\`'
alter = r'\s*alter\s+'
create = r'\s*create\s+'
use_db = {}


class DDL_COUNT(object):

    def __init__(self):
        '''获取settings中数据库连接信息用于连接数据库时用'''

        self.DBS = getattr(settings,'DATABASES')
        self.confall = self.DBS['default']
        self.USER = self.confall['USER']
        self.HOST = self.confall['HOST']
        self.PASSWORD = self.confall['PASSWORD']
        self.DB = self.confall['NAME']
        self.PORT = self.confall['PORT']

    def db_names(self,start_time,end_time):
        '''连接数据库，查询指定时间范围日志，创建库字典，匹配create与alter数目'''

        sql = """select sql_content from sql_workflow where create_time<='%s' and create_time>='%s' and status='已正常结束' and cluster_name='DEV环境'""" % (end_time, start_time)
        print(sql)
        db_conn = pymysql.connect(user=self.USER, host=self.HOST,port=int(self.PORT),db=self.DB, passwd=self.PASSWORD, charset="utf8")
        query = db_conn.cursor()
        try:
            query.execute(sql)
            q_all = query.fetchall()
            use_db.clear()
            if q_all:
                for s in q_all:
                    db_re = re.search(regex, str(s[0]), flags=re.IGNORECASE)
                    if db_re != None:
                        db = ((db_re.group(0).split('`')[1]).lower()).strip()
                        # print(i)
                        if db in use_db:
                            alter_count = self.db_ddls(alter, s)
                            use_db[db][0] += alter_count
                            create_count = self.db_ddls(create, s)
                            use_db[db][1] += create_count
                        else:
                            use_db[db] = [0, 0]
                            alter_count = self.db_ddls(alter, s)
                            use_db[db][0] += alter_count
                            create_count = self.db_ddls(create, s)
                            use_db[db][1] += create_count
                    else:
                        pass
            else:
                use_db.clear()

        except:
            print("数据库操作报错!")

        finally:
            db_conn.close()

        # for k in list(use_db.keys()):
        #     print(str(k) + " : alter  " + str(use_db[k][0]) + " create :  " + str(use_db[k][1]))
        #过滤掉两个值都为0的值
        db_dict = dict([k for k in use_db.items() if k[1][0] != 0 or k[1][1] != 0])
        return db_dict

    def db_ddls(self,ddl_sql, s):
        '''使用正则匹配ddl操作'''
        ddl_count = 0
        ddl_re = len(re.findall(ddl_sql, str(s[0]), flags=re.IGNORECASE))
        ddl_count = ddl_re
        if ddl_re:
            return ddl_count
        else:
            pass
        return ddl_count


# if __name__ == '__main__':
#     sql_count = ddlcount()
#     sql_count.db_names()
