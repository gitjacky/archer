# -*- coding: UTF-8 -*-
import logging
from django.http import JsonResponse
from django.contrib.auth.decorators import  permission_required
from .models import instance
from .dao import Dao

logger = logging.getLogger('default')
# 获取实例列表
@permission_required('sql.menu_instance', raise_exception=True)
def lists(request):
    limit = int(request.POST.get('limit'))
    offset = int(request.POST.get('offset'))
    type = request.POST.get('type')
    limit = offset + limit
    search = request.POST.get('search', '')

    if type:
        instances = instance.objects.filter(instance_name__contains=search, type=type)[offset:limit] \
            .values("id", "instance_name", "db_type", "type", "host", "port", "user")
        count = instance.objects.filter(instance_name__contains=search, type=type).count()
    else:
        instances = instance.objects.filter()[offset:limit] \
            .values("id", "instance_name", "db_type", "type", "host", "port", "user")
        count = instance.objects.filter().count()

    # QuerySet 序列化
    rows = [row for row in instances]

    result = {"total": count, "rows": rows}
    return JsonResponse(result)

# 获取实例用户列表
@permission_required('sql.menu_instance', raise_exception=True)
def users(request):
    instance_id = request.POST.get('instance_id')
    instance_name = instance.objects.get(id=instance_id).instance_name
    sql_get_user = '''select concat("\'", user, "\'", '@', "\'", host,"\'") as query from mysql.user;'''
    db_users = Dao().mysql_query(None,instance_name,'mysql', sql_get_user)
    # 获取用户权限信息
    data = []
    for db_user in db_users['rows']:
        user_info = {}
        user_priv = Dao().mysql_query(None,instance_name,'mysql', 'show grants for {};'.format(db_user[0]))['rows']
        user_info['user'] = db_user[0]
        user_info['privileges'] = user_priv
        data.append(user_info)
    # 关闭连接
    # dao.close()
    result = {'status': 0, 'msg': 'ok', 'data': data}
    return JsonResponse(result)
