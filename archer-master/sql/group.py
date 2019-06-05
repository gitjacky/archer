# -*- coding: UTF-8 -*-
from django.contrib.auth.models import Group
from django.db.models import F
from .models import instance, grouprelations,users
from django.http import HttpResponse,JsonResponse
import logging
import simplejson as json
import traceback
from .permission import superuser_required


logger = logging.getLogger('default')


# 获取用户关联资源组列表
def user_groups(user):
    if user.is_superuser == 1:
        group_list = [group for group in Group.objects.filter()]
    else:
        group_ids = [group['group_id'] for group in
                     grouprelations.objects.filter(object_id=user.id, object_type=0).values('group_id')]
        group_list = [group for group in Group.objects.filter(id__in=group_ids,)]
    return group_list

# 获取用户实例列表（通过资源组间接关联）
def user_instances(user, type):
    # 先获取用户关联资源组列表
    group_list = user_groups(user)
    group_ids = [group.id for group in group_list]
    if user.is_superuser == 1:
        instance_ids = [master['id'] for master in instance.objects.all().values('id')]
    else:
        # 获取资源组关联的实例列表
        instance_ids = [group['object_id'] for group in
                        grouprelations.objects.filter(group_id__in=group_ids, object_type=1).values('object_id')]
    # 获取实例信息
    if type == 'all':
        instances = instance.objects.filter(pk__in=instance_ids)
    else:
        instances = instance.objects.filter(pk__in=instance_ids, type=type)
    return instances


# 获取资源组内关联指定权限组的用户
def auth_group_users(auth_group_names, group_id):
    group_user_ids = [group['object_id'] for group in
                      grouprelations.objects.filter(group_id=group_id, object_type=0).values('object_id')]

    group_users = users.objects.filter(groups__name__in=auth_group_names, id__in=group_user_ids)
    return group_users


# 获取资源组列表
@superuser_required
def group(request):
    limit = int(request.POST.get('limit'))
    offset = int(request.POST.get('offset'))
    limit = offset + limit
    search = request.POST.get('search', '')

    # 全部工单里面包含搜索条件
    group_list = Group.objects.filter(name__contains=search)[offset:limit].values("id","name")
    group_count = Group.objects.filter(name__contains=search).count()

    # QuerySet 序列化
    rows = [row for row in group_list]

    result = {"total": group_count, "rows": rows}
    # 返回查询结果
    return JsonResponse(result)


# 获取资源组已关联对象信息
def associated_objects(request):
    '''
    type：(0, '用户'), (1, '实例')
    '''
    group_id = int(request.POST.get('group_id'))
    object_type = request.POST.get('type')

    if object_type:
        rows = grouprelations.objects.filter(group_id=group_id, object_type=object_type).values(
            'id', 'object_id', 'object_name', 'group_id', 'group_name', 'object_type', 'create_time')
        count = grouprelations.objects.filter(group_id=group_id, object_type=object_type).count()
    else:
        rows = grouprelations.objects.filter(group_id=group_id).values(
            'id', 'object_id', 'object_name', 'group_id', 'group_name', 'object_type', 'create_time')
        count = grouprelations.objects.filter(group_id=group_id).count()
    rows = [row for row in rows]
    result = {'status': 0, 'msg': 'ok', "total": count, "rows": rows}
    return JsonResponse(result)


# 获取资源组未关联对象信息
def unassociated_objects(request):
    '''
    type：(0, '用户'), (1, '实例')
    '''
    group_id = int(request.POST.get('group_id'))
    object_type = int(request.POST.get('object_type'))

    associated_object_ids = [object_id['object_id'] for object_id in
                             grouprelations.objects.filter(group_id=group_id,
                                                           object_type=object_type).values('object_id')]

    if object_type == 0:
        unassociated_objects = users.objects.exclude(pk__in=associated_object_ids
                                                     ).annotate(object_id=F('pk'),
                                                                object_name=F('display')
                                                                ).values('object_id', 'object_name')
    elif object_type == 1:
        unassociated_objects = instance.objects.exclude(pk__in=associated_object_ids
                                                        ).annotate(object_id=F('pk'),
                                                                   object_name=F('instance_name')
                                                                   ).values('object_id', 'object_name')
    else:
        unassociated_objects = []

    rows = [row for row in unassociated_objects]

    result = {'status': 0, 'msg': 'ok', "rows": rows, "total": len(rows)}
    return JsonResponse(result)


# 获取资源组关联实例列表
def instances(request):
    group_name = request.POST.get('group_name')
    group_id = Group.objects.get(group_name=group_name).group_id
    type = request.POST.get('type')
    # 先获取资源组关联所有实例列表
    instance_ids = [group['object_id'] for group in
                    grouprelations.objects.filter(group_id=group_id, object_type=1).values('object_id')]

    # 获取实例信息
    instances_ob = instance.objects.filter(pk__in=instance_ids, type=type).values('id', 'instance_name')
    rows = [row for row in instances_ob]
    result = {'status': 0, 'msg': 'ok', "data": rows}
    return JsonResponse(result)


# 添加资源组关联对象
@superuser_required
def addrelation(request):
    '''
    type：(0, '用户'), (1, '角色'), (2, '主库'), (3, '从库')
    '''
    group_id = int(request.POST.get('group_id'))
    object_type = request.POST.get('object_type')
    object_list = json.loads(request.POST.get('object_info'))
    group_name = Group.objects.get(group_id=group_id).group_name
    try:
        grouprelations.objects.bulk_create(
            [grouprelations(object_id=int(object.split(',')[0]),
                            object_type=object_type,
                            object_name=object.split(',')[1],
                            group_id=group_id,
                            group_name=group_name) for object in object_list])
        result = {'status': 0, 'msg': 'ok'}
    except Exception as e:
        logger.error(traceback.format_exc())
        result = {'status': 1, 'msg': str(e)}
    return JsonResponse(result)