# -*- coding: UTF-8 -*-
import time
import subprocess
import logging
import traceback
from django.http import JsonResponse
from django.contrib.auth.decorators import  permission_required
from django.conf import settings
from .models import instance
from .config import SysConfig
from .aes_decryptor import Prpcrypt
from .dao import Dao

logger = logging.getLogger('default')

# 获取实例里面的数据库集合
def dbnamelist(request):
    instance_name = request.POST.get("instance_name","")
    result = {'status': 0, 'msg': 'ok', 'data': []}

    try:
        # 取出该实例的连接方式，为了后面连进去获取所有databases
        instance_info = instance.objects.get(instance_name=instance_name)
        instance_host = instance_info.host
        instance_port = int(instance_info.port)
        instance_user = instance_info.user
        instance_password = Prpcrypt().decrypt(instance_info.password)
        db_list = Dao().getAlldbByCluster(instance_host,instance_port,instance_user,instance_password)
        # 要把result转成JSON存进数据库里，方便SQL单子详细信息展示
        result['data'] = db_list
    except Exception as msg:
        result['status'] = 1
        result['msg'] = str(msg)

    return JsonResponse(result)

# 对比实例schema信息
@permission_required('sql.menu_schemasync', raise_exception=True)
def schemasync(request):
    instance_name = request.POST.get('instance_name')
    db_name = request.POST.get('db_name')
    target_instance_name = request.POST.get('target_instance_name')
    target_db_name = request.POST.get('target_db_name')
    sync_auto_inc = '--sync-auto-inc' if request.POST.get('sync_auto_inc') == 'true' else ''
    sync_comments = '--sync-comments' if request.POST.get('sync_comments') == 'true' else ''
    result = {'status': 0, 'msg': 'ok', 'data': []}

    #对比选项
    options = sync_auto_inc + ' ' + sync_comments

    # 循环对比全部数据库
    if db_name == 'all' or target_db_name == 'all':
        db_name = '*'
        target_db_name = '*'
    else:
        pass

    # 取出两个实例的连接方式
    instance_info = instance.objects.get(instance_name=instance_name)
    target_instance_info = instance.objects.get(instance_name=target_instance_name)

    # 获取对比结果文件
    path = SysConfig().sys_config.get('schemasync', '')
    timestamp = int(time.time())
    output_directory = settings.OUTPUT_DIR

    command = path + ' %s --output-directory=%s --tag=%s \
            mysql://%s:%s@%s:%d/%s  mysql://%s:%s@%s:%d/%s' % (options,
                                                               output_directory,
                                                               timestamp,
                                                               instance_info.user,
                                                               Prpcrypt().decrypt(instance_info.password),
                                                               instance_info.host,
                                                               instance_info.port,
                                                               db_name,
                                                               target_instance_info.user,
                                                               Prpcrypt().decrypt(target_instance_info.password),
                                                               target_instance_info.host,
                                                               target_instance_info.port,
                                                               target_db_name)

    try:
        diff = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                shell=True, universal_newlines=True)
        diff_stdout, diff_stderr = diff.communicate()
    except Exception as e:
        logger.error(traceback.format_exc())
        print(e)

    # 非全部数据库对比可以读取对比结果并在前端展示
    if db_name != '*':
        date = time.strftime("%Y%m%d", time.localtime())
        patch_sql_file = '%s%s_%s.%s.patch.sql' % (output_directory, target_db_name, timestamp, date)
        revert_sql_file = '%s%s_%s.%s.revert.sql' % (output_directory, target_db_name, timestamp, date)
        cat_patch_sql = subprocess.Popen(['cat', patch_sql_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, universal_newlines=True)
        cat_revert_sql = subprocess.Popen(['cat', revert_sql_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT, universal_newlines=True)
        patch_stdout, patch_stderr = cat_patch_sql.communicate()
        revert_stdout, revert_stderr = cat_revert_sql.communicate()
        result['data'] = {'diff_stdout': diff_stdout, 'patch_stdout': patch_stdout, 'revert_stdout': revert_stdout}
    else:
        result['data'] = {'diff_stdout': diff_stdout, 'patch_stdout': '', 'revert_stdout': ''}

    # 删除对比文件
    # subprocess.call(['rm', '-rf', patch_sql_file, revert_sql_file, 'schemasync.log'])
    return JsonResponse(result)

