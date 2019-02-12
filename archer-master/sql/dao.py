# -*- coding: UTF-8 -*- 

import MySQLdb

from django.db import connection
import logging,traceback
from .models import master_config
from .aes_decryptor import Prpcrypt
import time

logger = logging.getLogger('default')

class Dao(object):
    _CHART_DAYS = 90

    #连进指定的mysql实例里，读取所有databases并返回
    def getAlldbByCluster(self, masterHost, masterPort, masterUser, masterPassword):
        listDb = []
        conn = None
        cursor = None
        
        try:
            conn=MySQLdb.connect(host=masterHost, port=masterPort, user=masterUser, passwd=masterPassword, charset='utf8mb4')
            cursor = conn.cursor()
            sql = "show databases"
            n = cursor.execute(sql)
            listDb = [row[0] for row in cursor.fetchall() 
                         if row[0] not in ('information_schema', 'performance_schema', 'mysql', 'test')]
        except MySQLdb.Warning as w:
            print(str(w))
        except MySQLdb.Error as e:
            print(str(e))
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.commit()
                conn.close()
        return listDb

    def getWorkChartsByMonth(self):
        cursor = connection.cursor()
        sql = "select date_format(create_time, '%%m-%%d'),count(*) from sql_workflow where create_time>=date_add(now(),interval -%s day) group by date_format(create_time, '%%m-%%d') order by 1 asc;" % (Dao._CHART_DAYS)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def getWorkChartsByPerson(self):
        cursor = connection.cursor()
        sql = "select engineer, count(*) as cnt from sql_workflow where create_time>=date_add(now(),interval -%s day) group by engineer order by cnt desc limit 50;" % (Dao._CHART_DAYS)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def getCancelChartsByPerson(self):
        cursor = connection.cursor()
        sql = "select engineer, count(*) as cnt from sql_workflow where create_time>=date_add(now(),interval -%s day) and status='人工终止流程' group by engineer order by cnt desc limit 50;" % (Dao._CHART_DAYS)
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

   ##liucb ddl统计
    def getworkChartsddl(self):
        engineers = {}
        alter_result = workflow.objects.filter(cluster_name='DEV环境',status='已正常结束',sql_content__icontains='alter')


    # 根据集群名获取主库连接字符串，并封装成一个dict
    def getMasterConnStr(self,clusterName):
        listMasters = master_config.objects.filter(cluster_name=clusterName)

        masterHost = listMasters[0].master_host
        masterPort = listMasters[0].master_port
        masterUser = listMasters[0].master_user
        masterPassword = Prpcrypt().decrypt(listMasters[0].master_password)
        dictConn = {'masterHost': masterHost, 'masterPort': masterPort, 'masterUser': masterUser,
                    'masterPassword': masterPassword}
        return dictConn

    # 连进指定的mysql实例里，执行sql并返回
    def mysql_execute(self,clustername,sql):
        result = {}
        dictConn = self.getMasterConnStr(clustername)
        try:
            conn = MySQLdb.connect(host=dictConn['masterHost'], port=dictConn['masterPort'], user=dictConn['masterUser'], passwd=dictConn['masterPassword'],
                                   charset='utf8')
            cursor = conn.cursor()
            sql_list = [e_sql for e_sql in sql.split('\n') if e_sql != '' and e_sql != '\r']
            try:
                for i,v in enumerate(sql_list):
                    t_start = time.time()
                    cursor.execute(v)
                    result[i] = cursor.rowcount
                    result[i] = [result[i], bool(cursor._executed)]
                    conn.commit()
                    t_end = time.time()
                    execute_time = "%5s" % "{:.4f}".format(t_end - t_start)
                    result[i].append(execute_time)
            except Exception as e:
                conn.rollback()
                result[i] = (str(e)).split(',')

            finally:
                cursor.close()
                conn.close()

        except Exception as e:
            logger.error(traceback.format_exc())
            result = e

        return result

