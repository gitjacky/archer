# -*- coding: UTF-8 -*- 

import re
import json, os
import datetime
import logging, traceback
from collections import OrderedDict
import ldap
import time
from django.db import connection

from django.db.models import Q
from django.conf import settings
from django.core import serializers  # Jacky
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout

from .dao import Dao
from .const import Const
from .sendmail import MailSender
from .inception import InceptionDao
from .aes_decryptor import Prpcrypt
from .models import users, master_config, workflow, workrelease, detailrecords, rel_memo, mongo_config, mogocode, \
    mongolog
from .views import getMasterConnStr, getNow, _getDetailUrl
from .ddl_count import DDL_COUNT
from django.db import transaction
from .mogo_sync import SyncSc
from .config import SysConfig

logger = logging.getLogger('default')
dao = Dao()
inceptionDao = InceptionDao()
prpCryptor = Prpcrypt()
login_failure_counter = {}  # 登录失败锁定计数器，给ldapAuthenticate用
sqlSHA1_cache = {}  # 存储SQL文本与SHA1值的对应关系，尽量减少与数据库的交互次数,提高效率。格式: {工单ID1:{SQL内容1:sqlSHA1值1, SQL内容2:sqlSHA1值2},}


# ajax接口，登录页面调用，用来验证用户名密码
@csrf_exempt
def ldapAuthenticate(username, password):
    # ldap认证
    server = "ldap://192.168.2.2:389"
    d_name = 'NKXTX\\' + username
    baseDN = "ou=HQ_Org_Info_Center,ou=Kx_Org_HQ_UserS,ou=Kx_Org_UserS,dc=nkxtx,dc=com"
    searchScope = ldap.SCOPE_SUBTREE
    searchFilter = "sAMAccountName=" + username
    retrieveAttributes = ['mail', 'cn', 'sAMAccountName']
    conn = ldap.initialize(server)
    conn.set_option(ldap.OPT_REFERRALS, 0)
    conn.protocol_version = ldap.VERSION3

    try:
        conn.simple_bind_s(d_name, password)
        ldap_result_id = conn.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        ret = 1
    except ldap.LDAPError as e:
        ldap_result_id = ''
        ret = 0

    # ldap中登陆成功
    if ret:

        # 用户在系统中存在
        userobj = users.objects.filter(username=username)

        if len(userobj) > 0:
            local_info = locallogin(username, password)
            # 系统中登陆失败,更新密码
            if local_info['status'] == 1:
                userobj.password = make_password(password)
                userobj.save()
            else:
                pass
            result = {'status': 0, 'msg': 'ok', 'data': ''}
        # 用户在系统中不存在
        else:
            if ldap_result_id:
                result_type, result_data = conn.result(ldap_result_id, 0)
                mail = (result_data[0][1]['mail'][0]).decode('utf-8')
                displayname = (result_data[0][1]['cn'][0]).decode('utf-8')

                user = users(username=username, password=make_password(password), email=mail, display=displayname)
                user.save()
                mygroup = Group.objects.get(name='工程师')
                mygroup.user_set.add(user)
                conn.unbind()
                result = {'status': 0, 'msg': 'ok', 'data': user}
            else:
                conn.unbind()
                result = {'status': 1, 'msg': '用户名或密码错误，请重新输入！', 'data': ''}
    else:
        result = locallogin(username, password)

    return result


@csrf_exempt
def locallogin(username, password):
    """登录认证，包含一个登录失败计数器，5分钟内连续失败5次的账号，会被锁定5分钟"""

    # 服务端二次验证参数
    if username == "" or password == "" or username is None or password is None:
        result = {'status': 2, 'msg': '登录用户名或密码为空，请重新输入!', 'data': ''}
    elif username in login_failure_counter and login_failure_counter[username][
        "cnt"] >= settings.LOCK_CNT_THRESHOLD and (datetime.datetime.now() - login_failure_counter[username][
        "last_failure_time"]).seconds <= settings.LOCK_TIME_THRESHOLD:
        result = {'status': 3, 'msg': '登录失败超过5次，该账号已被锁定5分钟!', 'data': ''}
    else:
        user = authenticate(username=username, password=password)
        if user:
            if username in login_failure_counter:
                # 如果登录失败计数器中存在该用户名，则清除之
                login_failure_counter.pop(username)
            result = {'status': 0, 'msg': 'ok', 'data': user}
        else:
            if username not in login_failure_counter:
                # 第一次登录失败，登录失败计数器中不存在该用户，则创建一个该用户的计数器
                login_failure_counter[username] = {"cnt": 1, "last_failure_time": datetime.datetime.now()}
            else:
                if (datetime.datetime.now() - login_failure_counter[username][
                    "last_failure_time"]).seconds <= settings.LOCK_TIME_THRESHOLD:
                    login_failure_counter[username]["cnt"] += 1
                else:
                    # 上一次登录失败时间早于5分钟前，则重新计数。以达到超过5分钟自动解锁的目的。
                    login_failure_counter[username]["cnt"] = 1
                login_failure_counter[username]["last_failure_time"] = datetime.datetime.now()
            result = {'status': 1, 'msg': '用户名或密码错误，请重新输入！', 'data': ''}

    return result


# ajax接口，登录页面调用，用来验证用户名密码
@csrf_exempt
def authenticateEntry(request):
    """接收http请求，然后把请求中的用户名密码传给ldapAuthenticate去验证"""
    if request.is_ajax():
        username = request.POST.get('username')
        password = request.POST.get('password')
    else:
        username = request.POST['username']
        password = request.POST['password']

    if settings.ENABLE_LDAP:
        result = ldapAuthenticate(username, password)
    else:
        result = locallogin(username, password)
    if result['status'] == 0:

        # 调用了django内置登录方法，防止管理后台二次登录
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)

        result = {'status': 0, 'msg': 'ok', 'data': None}
        request.session['login_username'] = username
    return HttpResponse(json.dumps(result), content_type='application/json')


# 提交SQL给inception进行自动审核
@csrf_exempt
def simplecheck(request):
    if request.is_ajax():
        sqlContent = request.POST.get('sql_content')
        clusterName = request.POST.get('cluster_name')
    else:
        sqlContent = request.POST['sql_content']
        clusterName = request.POST['cluster_name']

    finalResult = {'status': 0, 'msg': 'ok', 'data': []}
    # 服务器端参数验证
    if sqlContent is None or clusterName is None:
        finalResult['status'] = 1
        finalResult['msg'] = '页面提交参数可能为空'
        return HttpResponse(json.dumps(finalResult), content_type='application/json')

    sqlContent = sqlContent.rstrip()
    if sqlContent[-1] != ";":
        finalResult['status'] = 1
        finalResult['msg'] = 'SQL语句结尾没有以;结尾，请重新修改并提交！'
        return HttpResponse(json.dumps(finalResult), content_type='application/json')
    # 交给inception进行自动审核
    try:
        result = inceptionDao.sqlautoReview(sqlContent, clusterName)
    except Exception as e:
        logger.error(traceback.format_exc())
        result = []
        result['status'] = 1
        result['msg'] = str(e)
        return HttpResponse(json.dumps(result), content_type='application/json')

    if result is None or len(result) == 0:
        finalResult['status'] = 1
        finalResult['msg'] = 'inception返回的结果集为空！可能是SQL语句有语法错误!'
        return HttpResponse(json.dumps(finalResult), content_type='application/json')
    # 要把result转成JSON存进数据库里，方便SQL单子详细信息展示
    list_result = [list(x) for x in result]
    sql_str = len(list_result)
    latest_re = 'latest_time'
    create_re = r'create\s+table'
    for i in range(sql_str):
        if i > 0:
            create_result = re.search(create_re, list_result[i][5], flags=re.IGNORECASE)
            latest_result = re.search(latest_re, list_result[i][5], flags=re.IGNORECASE)
            if create_result and latest_result:
                print("ok")
            elif create_result and not latest_result:
                if list_result[i][4] == "None":
                    list_result[i][4] = "\nPlease add public column latest_time."
                else:
                    list_result[i][4] = list_result[i][4] + "\nPlease add public column latest_time."
            else:
                print("not create")
        else:
            pass
    finalResult['data'] = list_result

    return HttpResponse(json.dumps(finalResult), content_type='application/json')


# 请求图表数据
@csrf_exempt
def getMonthCharts(request):
    result = dao.getWorkChartsByMonth()
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def getPersonCharts(request):
    result = dao.getWorkChartsByPerson()
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def getCancelCharts(request):
    result = dao.getCancelChartsByPerson()
    return HttpResponse(json.dumps(result), content_type='application/json')


def getSqlSHA1(workflowId):
    """调用django ORM从数据库里查出review_content，从其中获取sqlSHA1值"""
    workflowDetail = get_object_or_404(workflow, pk=workflowId)
    dictSHA1 = {}
    # 使用json.loads方法，把review_content从str转成list,
    listReCheckResult = json.loads(workflowDetail.review_content)

    for rownum in range(len(listReCheckResult)):
        id = rownum + 1
        sqlSHA1 = listReCheckResult[rownum][10]
        if sqlSHA1 != '':
            dictSHA1[id] = sqlSHA1

    if dictSHA1 != {}:
        # 如果找到有sqlSHA1值，说明是pt-OSC操作的，将其放入缓存。
        # 因为使用OSC执行的工单占较少数，所以不设置缓存过期时间
        sqlSHA1_cache[workflowId] = dictSHA1
    return dictSHA1


@csrf_exempt
def getOscPercent(request):
    """获取该SQL的pt-OSC执行进度和剩余时间"""
    workflowId = request.POST['workflowid']
    sqlID = request.POST['sqlID']
    if workflowId == '' or workflowId is None or sqlID == '' or sqlID is None:
        context = {"status": -1, 'msg': 'workflowId或sqlID参数为空.', "data": ""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    workflowId = int(workflowId)
    sqlID = int(sqlID)
    dictSHA1 = {}
    if workflowId in sqlSHA1_cache:
        dictSHA1 = sqlSHA1_cache[workflowId]
        # cachehit = "已命中"
    else:
        dictSHA1 = getSqlSHA1(workflowId)
        # cachehit = "未命中"

    if dictSHA1 != {} and sqlID in dictSHA1:
        sqlSHA1 = dictSHA1[sqlID]
        result = inceptionDao.getOscPercent(sqlSHA1)  # 成功获取到SHA1值，去inception里面查询进度
        if result["status"] == 0:
            # 获取到进度值
            pctResult = result
        else:
            # result["status"] == 1,未获取到进度值，需要与workflow.execute_result对比，来判断是已经执行过了还是未执行
            execute_result = workflow.objects.get(id=workflowId).execute_result
            try:
                listExecResult = json.loads(execute_result)
            except ValueError:
                listExecResult = execute_result
            if type(listExecResult) == list and len(listExecResult) >= sqlID - 1:
                if dictSHA1[sqlID] in listExecResult[sqlID - 1][10]:
                    # 已经执行完毕，进度值置为100
                    pctResult = {"status": 0, "msg": "ok", "data": {"percent": 100, "timeRemained": ""}}
            else:
                # 可能因为前一条SQL是DML，正在执行中;或者还没执行到这一行。但是status返回的是4，而当前SQL实际上还未开始执行。这里建议前端进行重试
                pctResult = {"status": -3, "msg": "进度未知", "data": {"percent": -100, "timeRemained": ""}}
    elif dictSHA1 != {} and sqlID not in dictSHA1:
        pctResult = {"status": 4, "msg": "该行SQL不是由pt-OSC执行的", "data": ""}
    else:
        pctResult = {"status": -2, "msg": "整个工单不由pt-OSC执行", "data": ""}
    return HttpResponse(json.dumps(pctResult), content_type='application/json')


@csrf_exempt
def getWorkflowStatus(request):
    """获取某个工单的当前状态"""
    workflowId = request.POST['workflowid']
    if workflowId == '' or workflowId is None:
        context = {"status": -1, 'msg': 'workflowId参数为空.', "data": ""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    workflowId = int(workflowId)
    workflowDetail = get_object_or_404(workflow, pk=workflowId)
    workflowStatus = workflowDetail.status
    result = {"status": workflowStatus, "msg": "", "data": ""}
    return HttpResponse(json.dumps(result), content_type='application/json')


@csrf_exempt
def stopOscProgress(request):
    """中止该SQL的pt-OSC进程"""
    workflowId = request.POST['workflowid']
    sqlID = request.POST['sqlID']
    if workflowId == '' or workflowId is None or sqlID == '' or sqlID is None:
        context = {"status": -1, 'msg': 'workflowId或sqlID参数为空.', "data": ""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    loginUser = request.session.get('login_username', False)
    workflowDetail = workflow.objects.get(id=workflowId)
    try:
        listAllReviewMen = json.loads(workflowDetail.review_man)
    except ValueError:
        listAllReviewMen = (workflowDetail.review_man,)
    # 服务器端二次验证，当前工单状态必须为等待人工审核,正在执行人工审核动作的当前登录用户必须为审核人. 避免攻击或被接口测试工具强行绕过
    if workflowDetail.status != Const.workflowStatus['executing']:
        context = {"status": -1, "msg": '当前工单状态不是"执行中"，请刷新当前页面！', "data": ""}
        return HttpResponse(json.dumps(context), content_type='application/json')
    if loginUser is None or loginUser not in listAllReviewMen:
        context = {"status": -1, 'msg': '当前登录用户不是审核人，请重新登录.', "data": ""}
        return HttpResponse(json.dumps(context), content_type='application/json')

    workflowId = int(workflowId)
    sqlID = int(sqlID)
    if workflowId in sqlSHA1_cache:
        dictSHA1 = sqlSHA1_cache[workflowId]
    else:
        dictSHA1 = getSqlSHA1(workflowId)
    if dictSHA1 != {} and sqlID in dictSHA1:
        sqlSHA1 = dictSHA1[sqlID]
        optResult = inceptionDao.stopOscProgress(sqlSHA1)
    else:
        optResult = {"status": 4, "msg": "不是由pt-OSC执行的", "data": ""}
    return HttpResponse(json.dumps(optResult), content_type='application/json')


# 返回项目版本目录给前端版本发布的ajax/js并在前台下拉框展示 (jacky)
@csrf_exempt
def versioninfo(request):
    '''返回项目版本目录给前端并在前台下拉框展示'''
    loginUser = request.session.get('login_username', False)
    svn_p1 = request.GET.get('base_svn', None)
    print(svn_p1)
    if svn_p1 is None:
        return render(request, 'versionSql.html')
    else:
        # aa = '/mysvn'
        aa = '/data/svns/'
        svn_f1 = os.path.join(aa, svn_p1)

        last_path = os.path.split(svn_f1)[1]

        re_reg = re.compile(r'^\d+.\d+.\d+.\d+')
        re_path = re_reg.findall(last_path)

        # print(re_path)

        if os.path.exists(svn_f1) and len(re_path) == 0:
            pro_dir = [x for x in os.listdir(svn_f1) if
                       os.path.isdir(os.path.join(svn_f1, x)) and not x.startswith('.')]

        elif os.path.exists(svn_f1) and len(re_path) > 0:
            pro_dir = [x for x in os.listdir(svn_f1) if os.path.isfile(os.path.join(svn_f1, x))]
            pro_dir = [x for x in pro_dir if os.path.splitext(x)[1] == '.sql']
        else:
            pass
        # print(pro_dir)

        context = {'currentMenu': 'versions', 'loginUser': loginUser, 'pro_dir': pro_dir}
        return JsonResponse(context)


# 返回可用数据库连接，审核人信息给前端ajax/js  (jacky)
@csrf_exempt
def clustersandAudit(request):
    '''返回可用数据库连接，审核人信息给前端'''
    masters = master_config.objects.all().order_by('cluster_name')
    if len(masters) == 0:
        context = {'errMsg': '集群数为0，可能后端数据没有配置集群'}
        return render(request, 'error.html', context)

    # 获取所有集群名称
    listAllClusterName = [master.cluster_name for master in masters if master.cluster_name != "DEV环境"]

    dictAllClusterDb = OrderedDict()
    # 每一个都首先获取主库地址在哪里
    for clusterName in listAllClusterName:
        listMasters = master_config.objects.filter(cluster_name=clusterName)
        if len(listMasters) != 1:
            context = {'errMsg': '存在两个集群名称一样的集群，请修改数据库'}
            return render(request, 'error.html', context)
        # 取出该集群的名称以及连接方式，为了后面连进去获取所有databases
        masterHost = listMasters[0].master_host
        masterPort = listMasters[0].master_port
        masterUser = listMasters[0].master_user
        masterPassword = prpCryptor.decrypt(listMasters[0].master_password)

        listDb = dao.getAlldbByCluster(masterHost, masterPort, masterUser, masterPassword)
        dictAllClusterDb[clusterName] = listDb

    # 获取所有审核人，当前登录用户不可以审核
    loginUser = request.session.get('login_username', False)
    reviewMen = users.objects.filter(role='审核人', is_active=1).exclude(username=loginUser)
    if len(reviewMen) == 0:
        context = {'errMsg': '审核人为0，请配置审核人'}
        return render(request, 'error.html', context)
    listAllReviewMen = [user.username for user in reviewMen]

    db_envs = [i for i in dictAllClusterDb]

    context = {'db_envs': db_envs, 'listAllReviewMen': listAllReviewMen}
    return JsonResponse(context)


# 获取所有版本工单内容(jacky)
@csrf_exempt
def allrelease(request):
    '''获取所有版本工单内容(jacky)'''
    # 一个页面展示
    page_limit = 15
    # pageNo = 0
    navStatus = request.POST.get('navStatus', 'allrelease')

    # 参数检查
    pageNo = request.POST.get('pageNo', '0')
    pageNo = pageNo.strip()

    if not isinstance(pageNo, str) or not isinstance(navStatus, str):
        raise TypeError('pageNo或navStatus传入参数不对')
    else:
        try:
            pageNo = int(pageNo) - 1
            if pageNo < 0:
                pageNo = 0
        except Exception as msg:
            logger.error(traceback.format_exc())
            context = {'errMsg': msg}
            return render(request, 'error.html', context)

    loginUser = request.session.get('login_username', False)
    # workrelease model，根据pageNo和navStatus获取对应的内容
    offset = pageNo * page_limit
    limit = offset + page_limit

    # 分角色查看全部工单,工程师只能看到自己发起的工单，审核人可以看到全部
    allWorkrel = []
    # 查询全部流程
    loginUserOb = users.objects.get(username=loginUser)
    role = loginUserOb.role

    if navStatus == 'allrelease' and role == '审核人':
        allWorkrel = workrelease.objects.all().values('id', 'release_name', 'release_path', 'deploy_env', 'submit_user',
                                                      'audit_user__username', 'submit_time', 'execute_status').order_by(
            '-submit_time')[offset:limit]
        allWorkrel = list(allWorkrel)

    elif navStatus == 'allrelease' and role == '工程师':
        allWorkrel = workrelease.objects.filter(submit_user=loginUser).values('id', 'release_name', 'release_path',
                                                                              'deploy_env', 'submit_user',
                                                                              'audit_user__username', 'submit_time',
                                                                              'execute_status').order_by(
            '-submit_time')[offset:limit]
        allWorkrel = list(allWorkrel)
    else:
        context = {'errMsg': '传入的navStatus参数有误！'}
        return render(request, 'error.html', context)
    all_count = workrelease.objects.all().count()

    context = {'all_count': all_count, 'allWorkrel': allWorkrel, 'pageNo': pageNo, 'page_limit': page_limit,
               'role': role, 'navStatus': navStatus}
    return JsonResponse(context)


# 版本发布sql文件提交版本工单之后自动读取sql文件后做自动审核，提交SQL给inception进行解析(jacky)
@csrf_exempt
def relautoreview(request):
    '''自动读取sql文件后做自动审核，提交SQL给inception进行解析'''
    if request.method == 'POST':
        detail_id = request.POST.get('detail_id', False)
        rel_file = request.POST.get('rel_file', False)
    else:
        context = {'errMsg': '传入的方法有误！'}
        return render(request, 'error.html', context)

    if detail_id and rel_file:
        detailrec_obj = detailrecords.objects.get(id=int(detail_id))
        workrel_obj = workrelease.objects.get(id=int(detailrec_obj.release_version.id))
        workrel_obj.execute_status = ''
        workrel_obj.save()

        # 读取对应的sql文件内容并存放到数据库表字段sql_content中
        full_file = '/data/svns' + os.path.join(workrel_obj.release_path, rel_file)
    else:
        context = {'errMsg': '传入的参数有误！'}
        return render(request, 'error.html', context)

    # with open(full_file,encoding='utf-8-sig') as f:
    try:
        with open(full_file, "r", encoding="utf-8-sig", buffering=-1, closefd=True) as f:
            file_content = f.readlines()
            sqlContent = ''.join(file_content).strip()
            # sqlContent = (''.join(file_content)).replace("\n", "")
    except IOError as msg:
        logger.error(traceback.format_exc())
        with open(full_file, "r", encoding="utf-8", buffering=-1, closefd=True) as f:
            file_content = f.readlines()
            sqlContent = ''.join(file_content).strip()

    clusterName = detailrec_obj.cluster_name

    # 服务器端验证参数与sql内容是否有误

    finalResult = {'status': 0, 'msg': '自动审核结束', 'data': []}
    if sqlContent is None or clusterName is None:
        finalResult['status'] = 1
        finalResult['msg'] = '页面提交参数可能为空'
        finalResult['record_status'] = Const.workflowStatus['autoreviewwrong']
        detailrec_obj.status = finalResult['record_status']
        detailrec_obj.save()
        return JsonResponse(finalResult)
    elif sqlContent[-1] != ";":
        finalResult['status'] = 1
        finalResult['msg'] = 'SQL语句结尾没有以;结尾，请重新修改并提交！'
        finalResult['record_status'] = Const.workflowStatus['autoreviewwrong']
        detailrec_obj.status = finalResult['record_status']
        detailrec_obj.save()
        return JsonResponse(finalResult)
    else:
        # SQL内容存进数据库字段
        detailrec_obj.sql_content = sqlContent

    # 交给inception进行自动审核
    result = inceptionDao.sqlautoReview(sqlContent, clusterName, isBackup='否')

    if result is None or len(result) == 0:
        finalResult['status'] = 1
        finalResult['msg'] = 'inception返回的结果集为空！可能是SQL语句有语法错误'
        finalResult['record_status'] = Const.workflowStatus['autoreviewwrong']
        detailrec_obj.status = finalResult['record_status']
        detailrec_obj.save()
        return JsonResponse(finalResult)
    else:
        finalResult['data'] = result
        finalResult['record_status'] = Const.workflowStatus['manreviewing']
        detailrec_obj.status = finalResult['record_status']
        detailrec_obj.save()

    # 遍历result，看是否有任何自动审核不通过的地方，一旦有，则为自动审核不通过；没有的话，则为等待人工审核状态

    for row in result:
        if row[2] == 2:
            # 状态为2表示严重错误，必须修改
            detailrec_obj.status = Const.workflowStatus['autoreviewwrong']
            context = {'autoaudit_status': detailrec_obj.status}
            finalResult['record_status'] = Const.workflowStatus['autoreviewwrong']
            # return JsonResponse(context)
            # break
        elif re.match(r"\w*comments\w*", row[4]):
            print("row[4]:" + row[4])
            detailrec_obj.status = Const.workflowStatus['autoreviewwrong']
            context = {'autoaudit_status': detailrec_obj.status}
            # return JsonResponse(context)
            # break

    # 要把result转成JSON存进数据库里，方便SQL单子详细信息展示
    jsonResult = json.dumps(result)
    detailrec_obj.review_content = jsonResult
    detailrec_obj.save()
    return JsonResponse(finalResult)
    # context = {'autoaudit_status': detailrec_obj.status}
    # return JsonResponse(context)


# 版本sql详情页面查看详情信息(jacky)
@csrf_exempt
def resdetail(request):
    '''版本sql详情页面查看详情信息(jacky)'''
    detail_id = request.POST.get('detail_id')
    detail_contents = get_object_or_404(detailrecords, pk=detail_id)

    detailContent = None

    if detail_contents.status in (
    Const.workflowStatus['finish'], Const.workflowStatus['exception']) and detail_contents.execute_result != "":
        detailContent = json.loads(detail_contents.execute_result)

    elif detail_contents.status == Const.workflowStatus['manreviewing'] and detail_contents.review_content != "":
        detailContent = json.loads(detail_contents.review_content)

    elif detail_contents.status == Const.workflowStatus['abort'] or detail_contents.status == Const.workflowStatus[
        'executing']:
        detailContent = json.loads(detail_contents.review_content)

    elif detail_contents.status == Const.workflowStatus['autoreviewwrong'] and detail_contents.review_content == "":
        detailContent = ""

    elif detail_contents.status == Const.workflowStatus['autoreviewwrong'] and detail_contents.review_content != "":
        detailContent = json.loads(detail_contents.review_content)

    else:
        detailContent = ""

    context = {"detailContent": detailContent}
    return JsonResponse(context)


# 版本工单中获取dba备注信息
@csrf_exempt
def getmemo(request):
    '''版本sql详情页面点击修改备注获取dba备注信息(jacky)'''
    relid = request.POST.get('rsid')
    memos = get_object_or_404(rel_memo, rel_id=relid)
    dba_memo_content = memos.dba_memo

    context = {'dba_memo': dba_memo_content}
    return JsonResponse(context)


# 版本工单中添加dba备注信息
@csrf_exempt
def memosave(request):
    '''版本sql详情页面dba添加、修改备注信息(jacky)'''
    add_memo = request.POST.get('form_data')
    relid = request.POST.get('rsid')
    memos = get_object_or_404(rel_memo, rel_id=relid)
    memos.dba_memo = add_memo.strip('')
    memos.save()

    context = {'new_memo': memos.dba_memo}
    return JsonResponse(context)


# 版本工单人工审核也通过，执行SQL(jacky)
@csrf_exempt
def relsexecute(request):
    '''人工审核也通过，执行SQL(jacky)'''

    detailId = request.POST.get('execute_id')
    if detailId == '' or detailId is None:
        context = {'errMsg': '工单id参数为空.'}
        return render(request, 'error.html', context)

    detailObj = get_object_or_404(detailrecords, pk=int(detailId))
    clusterName = detailObj.cluster_name

    # 服务器端二次验证，正在执行人工审核动作的当前登录用户必须为审核人. 避免攻击或被接口测试工具强行绕过
    loginUser = request.session.get('login_username', False)
    AllReviewMen = users.objects.filter(role='审核人', is_active=1).values_list('username', flat=True)

    if loginUser is None or loginUser not in AllReviewMen:
        context = {'errMsg': '当前登录用户不是审核人，请重新登录.'}
        return render(request, 'error.html', context)
    else:
        detailObj.review_man = loginUser

    # 服务器端二次验证，当前工单状态必须为等待人工审核
    if detailObj.status != Const.workflowStatus['manreviewing']:
        context = {'errMsg': '当前工单状态不是等待人工审核中，请刷新当前页面！'}
        return render(request, 'error.html', context)

    dictConn = getMasterConnStr(clusterName)

    # 将流程状态修改为执行中，并更新reviewok_time字段
    detailObj.status = Const.workflowStatus['executing']
    detailObj.reviewok_time = getNow()
    detailObj.save()

    # 交给inception先split，再执行
    (finalStatus, finalList) = inceptionDao.executeFinal(detailObj, dictConn)

    # 封装成JSON格式存进数据库字段里
    strJsonResult = json.dumps(finalList)
    detailObj.execute_result = strJsonResult
    detailObj.finish_time = getNow()
    detailObj.status = finalStatus
    detailObj.save()

    # 检查本版本号中所有子脚本执行状态，然后更新版本记录的执行状态
    workrel = get_object_or_404(workrelease, id=detailObj.release_version.id)

    sub_count = detailrecords.objects.filter(release_version=detailObj.release_version.id).count()
    sub_fin_count = detailrecords.objects.filter(release_version=detailObj.release_version.id,
                                                 status=Const.workflowStatus['finish']).count()
    sub_can_count = detailrecords.objects.filter(release_version=detailObj.release_version.id,
                                                 status=Const.workflowStatus['abort']).count()
    sub_err_count = detailrecords.objects.filter(release_version=detailObj.release_version.id,
                                                 status=Const.workflowStatus['exception']).count()
    if sub_count == (sub_can_count + sub_fin_count) and sub_fin_count > 0:
        workrel.execute_status = Const.workflowStatus['finish']
        rel_version = detailObj.release_version.id
        title_prefix = "工单执行完毕"
        engineer = detailObj.engineer
        deploy_env = clusterName
        release_name = workrel.release_name
        execute_status = workrel.execute_status
        _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)

    elif sub_count == sub_can_count:
        workrel.execute_status = Const.workflowStatus['abort']
        rel_version = detailObj.release_version.id
        title_prefix = "工单终止执行"
        engineer = detailObj.engineer
        deploy_env = clusterName
        release_name = workrel.release_name
        execute_status = workrel.execute_status
        _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)

    elif sub_count == (sub_err_count + sub_fin_count):
        workrel.execute_status = Const.workflowStatus['exception']
        rel_version = detailObj.release_version.id
        title_prefix = "工单执行有异常"
        engineer = detailObj.engineer
        deploy_env = clusterName
        release_name = workrel.release_name
        execute_status = workrel.execute_status
        _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)

    else:
        workrel.execute_status = Const.workflowStatus['executing']
    workrel.audit_user = users.objects.get(username=loginUser)
    workrel.save()

    context = {"finalList": finalList, "finish_time": getNow(), "finalStatus": finalStatus}
    return HttpResponse(json.dumps(context))


# 获取工单文件的当前状态
@csrf_exempt
def getrelstatus(request):
    relId = request.POST.get('recordid')
    if relId == '' or relId is None:
        context = {'errMsg': '工单id参数为空.'}
        return render(request, 'error.html', context)

    detailObj = get_object_or_404(detailrecords, pk=int(relId)).status

    context = {"detailObj": detailObj}
    return JsonResponse(context)


def _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status):
    mailSender = MailSender()
    if hasattr(settings, 'MAIL_ON_OFF') == True:
        if getattr(settings, 'MAIL_ON_OFF') == "on":
            re_detail = re.compile("detail")
            url = _getDetailUrl(request) + str(rel_version) + '/'
            s_url = re_detail.sub("relsdetail", url)

            strTitle = "【inception】版本SQL" + title_prefix + "# " + str(rel_version)

            listAllReviewMen = users.objects.filter(role="审核人", is_active=1).exclude(username="kxtxdba")
            reviewer = [reviewer.username for reviewer in listAllReviewMen]
            reviewer_email = [reviewer.email for reviewer in listAllReviewMen]

            if title_prefix == "上线工单提醒":
                strContent = "发起人：" + engineer + "\n审核人：" + ','.join(
                    reviewer) + "\n上线环境: " + deploy_env + "\n工单地址：" + s_url + "\n工单名称：" + release_name
                mailSender.sendEmail(strTitle, strContent, reviewer_email)

            elif title_prefix == "工单执行完毕" or title_prefix == "工单终止执行" or title_prefix == "工单执行有异常":
                strContent = "发起人：" + engineer + "\n审核人：" + ','.join(
                    reviewer) + "\n上线环境: " + deploy_env + "\n工单地址：" + s_url + "\n工单名称：" + release_name + "\n执行结果: " + execute_status
                engineer_mail = users.objects.get(username=engineer).email
                reviewer_email.append(engineer_mail)
                mailSender.sendEmail(strTitle, strContent, reviewer_email)

            elif title_prefix == "编码同步提醒" or title_prefix == "接口同步完毕" or title_prefix == "定时器同步完毕" or title_prefix == "MQ同步完毕" or title_prefix == "接口同步中止":
                strContent = "发起人：" + engineer + "\n审核人：" + ','.join(
                    reviewer) + "\n目标环境: " + deploy_env + "\n执行结果: " + execute_status
                engineer_mail = users.objects.get(username=engineer).email
                reviewer_email.append(engineer_mail)
                strTitle = "【inception】" + title_prefix + "# " + str(rel_version)
                mailSender.sendEmail(strTitle, strContent, reviewer_email)

            else:
                pass
                # 给除了kxtxdba之外的审核人每人发一封邮件
                # mailSender.sendEmail(strTitle, strContent, [reviewer.email])
        else:
            # 不发邮件
            pass
    else:
        print("MAIL_ON_OFF off!")


# 版本sql终止执行(Jacky)
@csrf_exempt
def relstop(request):
    '''版本sql中，查看详情页面中中止执行按钮'''
    if request.is_ajax():
        record_id = request.POST.get("recordid")
    else:
        record_id = request.POST["recordid"]
    loginUser = request.session.get("login_username", False)
    stopObj = get_object_or_404(detailrecords, pk=int(record_id))
    stopObj.review_man = loginUser
    stopObj.status = Const.workflowStatus['abort']
    stopObj.finish_time = getNow()
    stopObj.save()
    stop_status = Const.workflowStatus['abort']

    # 检查本版本号中所有子脚本执行状态，然后更新版本记录的执行状态
    workrel = get_object_or_404(workrelease, id=stopObj.release_version.id)

    sub_count = detailrecords.objects.filter(release_version=stopObj.release_version.id).count()
    sub_fin_count = detailrecords.objects.filter(release_version=stopObj.release_version.id,
                                                 status=Const.workflowStatus['finish']).count()
    sub_can_count = detailrecords.objects.filter(release_version=stopObj.release_version.id,
                                                 status=Const.workflowStatus['abort']).count()
    sub_err_count = detailrecords.objects.filter(release_version=stopObj.release_version.id,
                                                 status=Const.workflowStatus['exception']).count()
    if sub_count == (sub_can_count + sub_fin_count) and sub_fin_count > 0:
        workrel.execute_status = Const.workflowStatus['finish']
        rel_version = stopObj.release_version.id
        title_prefix = "工单执行完毕"
        engineer = stopObj.engineer
        deploy_env = stopObj.cluster_name
        release_name = workrel.release_name
        execute_status = workrel.execute_status
        _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)

    elif sub_count == sub_can_count:
        workrel.execute_status = Const.workflowStatus['abort']
        rel_version = stopObj.release_version.id
        title_prefix = "工单终止执行"
        engineer = stopObj.engineer
        deploy_env = stopObj.cluster_name
        release_name = workrel.release_name
        execute_status = workrel.execute_status
        _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)

    elif sub_count == (sub_err_count + sub_fin_count):
        workrel.execute_status = Const.workflowStatus['exception']
        rel_version = stopObj.release_version.id
        title_prefix = "工单执行有异常"
        engineer = stopObj.engineer
        deploy_env = stopObj.cluster_name
        release_name = workrel.release_name
        execute_status = workrel.execute_status
        _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)

    else:
        workrel.execute_status = Const.workflowStatus['executing']
    workrel.audit_user = users.objects.get(username=loginUser)
    workrel.save()

    context = {"status": stop_status, "record_id": record_id, "finish_time": stopObj.finish_time}
    return JsonResponse(context)


# 提交项目版本目录发布工单
# @csrf_exempt
def versionsql(request):
    if request.method == 'POST':
        work_rels = workrelease()
        loginUser = request.session.get('login_username', False)

        svn_p = request.POST.get('svn_path')
        p_name = request.POST.get('p_name')
        s_name = request.POST.get('s_name')
        ver_name = request.POST.get('ver_name', False)
        d_event = request.POST.get('d_envirment')
        print(d_event)

        if ver_name != "is-empty" and ver_name != False:
            # 检查是否已存在待审核数据
            version_obj = workrelease.objects.filter(release_name=request.POST.get('workflow_name'),
                                                     deploy_env=request.POST.get('d_envirment'),
                                                     submit_user=loginUser, execute_status="")
            if len(version_obj) >= 1:
                msg = '该工单当前状态为待审核，请勿重复提交!'
                context = {'msg': msg}
                return JsonResponse(context)
            else:
                work_rels.release_path = os.path.join('/', svn_p, p_name, s_name, ver_name)
        else:
            work_rels.release_path = os.path.join('/', svn_p, p_name, s_name)
        print(work_rels.release_path)
        work_rels.release_name = request.POST.get('workflow_name')
        work_rels.deploy_env = request.POST.get('d_envirment')
        work_rels.submit_user = loginUser

        review_man = request.POST.get('review_man')
        work_rels.audit_user = users.objects.get(username=review_man)

        work_rels.release_status = Const.workflowStatus['autoreviewwait']
        work_rels.save()

        # 子表
        release_files = list((request.POST.get('sql_list')).split(','))
        rel_version = workrelease.objects.filter(release_name=request.POST.get('workflow_name')).order_by('-id')[0]

        # 备注表信息
        relmemo_obj = rel_memo()
        relmemo_obj.rel_id = rel_version
        dev_memo = request.POST.get('relmemo', '')
        if dev_memo:
            relmemo_obj.memo = dev_memo.strip('')
        relmemo_obj.save()

        if release_files:
            for release_file in release_files:
                # 循环对每条记录进行实例化
                obj = detailrecords(engineer=loginUser, review_man=review_man,
                                    status=Const.workflowStatus['autoreviewwait'], release_version=rel_version,
                                    release_file=release_file, cluster_name=request.POST.get('d_envirment'))
                obj.save()
                # recos.review_content = json.dumps()
                # recos.sql_content =
                # recos.execute_result =
            rel_version = rel_version.id
            title_prefix = "上线工单提醒"
            engineer = work_rels.submit_user
            deploy_env = work_rels.deploy_env
            release_name = work_rels.release_name
            execute_status = ''
            _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)

            return JsonResponse({'msg': "提交成功!"})

        else:
            return JsonResponse({'msg': "提交失败!"})

        context = {'currentMenu': 'versions', 'msg': 'success'}
    else:
        context = {'currentMenu': 'versions'}

    return render(request, 'versionSql.html', context)


# 开发环境ddl统计
@csrf_exempt
def ddlajx(request):
    if request.method == 'POST':
        start_time = request.POST.get('s_time', False)
        end_time = request.POST.get('e_time', False)
        if start_time == '' and end_time == '':
            end_time = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
            start_time = end_time + datetime.timedelta(days=-6)

        # 给定统计时间范围后，统计DDL
        ddlcount = DDL_COUNT()
        ddl_dict = ddlcount.db_names(start_time, end_time)

    context = {'currentMenu': 'ddlcount', "ddl_dict": ddl_dict}

    return JsonResponse(context)


# 获取版本工单信息用于上线其他环境
@csrf_exempt
def getrelinfo(request):
    if request.method == 'POST':
        rels_id = request.POST.get('rsid', False)
        rel_name = request.POST.get('rel_name', False)
        submit_user = request.POST.get('suser', False)
        other_env = request.POST.get('other_env', False)
    else:
        pass

    masters = list(master_config.objects.all().values_list('cluster_name', flat=True))

    if len(masters) == 0:
        context = {'errMsg': '集群数为0，可能后端数据没有配置集群'}
        return render(request, 'error.html', context)
    else:
        pass

    old_detailrec = list(
        detailrecords.objects.filter(release_version=int(rels_id)).values_list('release_file', flat=True))
    old_memo = list(rel_memo.objects.filter(rel_id=int(rels_id)).values_list('memo', flat=True))

    context = {'masters': masters, 'old_detailrec': old_detailrec, 'old_memo': old_memo}

    return JsonResponse(context)


# 版本工单上线其他环境
@csrf_exempt
def relother(request):
    if request.method == 'POST':
        rels_id = request.POST.get('rsid', False)
        rel_name = request.POST.get('rel_name', False)
        loginUser = request.session.get('login_username', False)
        other_env = request.POST.get('env', False)
        other_memo = request.POST.get('memo', False)

    review_dba = 'kxtxdba'
    review_man = users.objects.get(username=review_dba)

    transaction.set_autocommit(False)
    try:
        # 版本表
        rels_other = workrelease()
        relsObj = get_object_or_404(workrelease, pk=int(rels_id))
        rels_other.release_name = rel_name
        rels_other.release_path = relsObj.release_path
        rels_other.deploy_env = other_env
        rels_other.submit_user = loginUser
        rels_other.audit_user = review_man
        rels_other.submit_time = getNow()
        rels_other.save()

        # 详情表
        rel_version = workrelease.objects.filter(release_name=rel_name).order_by('-id')[0]
        detail_files = list(
            detailrecords.objects.filter(release_version=rels_id).values_list('release_file', flat=True))
        if detail_files:
            for rs_file in detail_files:
                # 循环对每条记录进行实例化
                detailobj = detailrecords(engineer=loginUser, review_man=review_man,
                                          status=Const.workflowStatus['autoreviewwait'], release_version=rel_version,
                                          release_file=rs_file, cluster_name=other_env)
                detailobj.save()
        else:
            pass
        # memo表
        # dev_memo = rel_memo.objects.get(rel_id=rels_id).memo
        dba_comm = rel_memo.objects.get(rel_id=rels_id).dba_memo
        rememo_obj = rel_memo(rel_id=rel_version, memo=other_memo.strip(''), dba_memo=dba_comm.strip(''))
        rememo_obj.save()

        transaction.commit()

        context = {'stat': '提交成功！'}
        return JsonResponse(context)
    except:
        transaction.rollback()
        context = {'stat': '提交失败！'}
        return JsonResponse(context)
    finally:
        transaction.set_autocommit(True)


# 选定指定环境查看工单列表
@csrf_exempt
def relfilter(request):
    '''获取所有版本工单内容(jacky)'''
    # 一个页面展示
    page_limit = 15
    # pageNo = 0
    navStatus = request.POST.get('navStatus', 'allrelease')
    env_value = request.POST.get('selectenv', False)
    if env_value:
        env_value = str(env_value).strip()
        env_value = env_value[0:3]
    else:
        context = {'errMsg': '未选择过滤环境!'}
        return render(request, 'error.html', context)
    # 参数检查
    pageNo = request.POST.get('pageNo', '0')
    pageNo = pageNo.strip()
    start_time = request.POST.get('s_time', False)
    end_time = request.POST.get('e_time', False)

    if not isinstance(pageNo, str) or not isinstance(navStatus, str):
        raise TypeError('pageNo或navStatus传入参数不对')
    else:
        try:
            pageNo = int(pageNo) - 1
            if pageNo < 0:
                pageNo = 0
        except Exception as msg:
            logger.error(traceback.format_exc())
            context = {'errMsg': msg}
            return render(request, 'error.html', context)

    loginUser = request.session.get('login_username', False)
    # workrelease model，根据pageNo和navStatus获取对应的内容
    offset = pageNo * page_limit
    limit = offset + page_limit

    # 分角色查看全部工单,工程师只能看到自己发起的工单，审核人可以看到全部
    allWorkrel = []
    # 查询全部流程
    loginUserOb = users.objects.get(username=loginUser)
    role = loginUserOb.role
    all_count = 0
    if env_value == "all" and role == '审核人':
        all_count = workrelease.objects.filter(submit_time__gt=start_time, submit_time__lt=end_time).count()
        allWorkrel = workrelease.objects.filter(submit_time__gt=start_time, submit_time__lt=end_time).values('id',
                                                                                                             'release_name',
                                                                                                             'release_path',
                                                                                                             'deploy_env',
                                                                                                             'submit_user',
                                                                                                             'audit_user__username',
                                                                                                             'submit_time',
                                                                                                             'execute_status').order_by(
            '-submit_time')[offset:limit]
        allWorkrel = list(allWorkrel)

    elif env_value == "all" and role == '工程师':
        all_count = workrelease.objects.filter(submit_user=loginUser, submit_time__gt=start_time,
                                               submit_time__lt=end_time).count()
        allWorkrel = workrelease.objects.filter(submit_user=loginUser, submit_time__gt=start_time,
                                                submit_time__lt=end_time).values('id', 'release_name', 'release_path',
                                                                                 'deploy_env', 'submit_user',
                                                                                 'audit_user__username', 'submit_time',
                                                                                 'execute_status').order_by(
            '-submit_time')[offset:limit]
        allWorkrel = list(allWorkrel)

    else:

        if navStatus == 'allrelease' and role == '审核人':
            all_count = workrelease.objects.filter(deploy_env__istartswith=env_value, submit_time__gt=start_time,
                                                   submit_time__lt=end_time).count()
            allWorkrel = workrelease.objects.filter(deploy_env__istartswith=env_value, submit_time__gt=start_time,
                                                    submit_time__lt=end_time).values('id', 'release_name',
                                                                                     'release_path', 'deploy_env',
                                                                                     'submit_user',
                                                                                     'audit_user__username',
                                                                                     'submit_time',
                                                                                     'execute_status').order_by(
                '-submit_time')[offset:limit]
            allWorkrel = list(allWorkrel)

        elif navStatus == 'allrelease' and role == '工程师':
            all_count = workrelease.objects.filter(submit_user=loginUser, deploy_env__istartswith=env_value,
                                                   submit_time__gt=start_time,
                                                   submit_time__lt=end_time).count()
            allWorkrel = workrelease.objects.filter(submit_user=loginUser, deploy_env__istartswith=env_value,
                                                    submit_time__gt=start_time, submit_time__lt=end_time).values('id',
                                                                                                                 'release_name',
                                                                                                                 'release_path',
                                                                                                                 'deploy_env',
                                                                                                                 'submit_user',
                                                                                                                 'audit_user__username',
                                                                                                                 'submit_time',
                                                                                                                 'execute_status').order_by(
                '-submit_time')[offset:limit]
            allWorkrel = list(allWorkrel)
        else:
            context = {'errMsg': '传入的navStatus参数有误！'}
            return render(request, 'error.html', context)

    context = {'all_count': all_count, 'allWorkrel': allWorkrel, 'pageNo': pageNo, 'page_limit': page_limit,
               'role': role, 'navStatus': navStatus}
    return JsonResponse(context)


# 获取环境
@csrf_exempt
def mgadd(request):
    if request.method == 'POST':
        loginUser = request.session.get('login_username', False)
        mghosts = list(mongo_config.objects.all().values_list('db_name', flat=True))
        if len(mghosts) == 0:
            context = {'errMsg': '可用连接为0，可能后端数据没有配置！'}
            return render(request, 'error.html', context)
        else:
            context = {'mghosts': mghosts, 'loginUser': loginUser}
            return JsonResponse(context)
    else:
        context = {'errMsg': '你的访问方式非法！'}
        return render(request, 'error.html', context)


# 提交mongo编码
@csrf_exempt
def mgcommit(request):
    if request.method == 'POST':
        mg_name = str(request.POST.get('mg_name', False)).strip()
        mg_type = int(request.POST.get('mg_type', False))
        s_env = request.POST.get('s_env', False)
        t_env = request.POST.get('t_env', False)
        loginuser = request.session.get('login_username', False)

    review_dba = 'kxtxdba'
    reviewer_obj = users.objects.get(username=review_dba)
    transaction.set_autocommit(False)
    try:
        mogoobj = mogocode(mogo_name=mg_name, mogo_type=mg_type, mogo_submit=loginuser, mogo_audit=reviewer_obj,
                           mogo_stat=Const.mogostat['waiting'], mogo_subtime=getNow(), mogo_source=s_env,
                           mogo_target=t_env)
        mogoobj.save()
        mglogobj = mongolog(audit_id=mogoobj, operation_type=0, operation_type_desc='提交工单', operation_info='等待操作人员处理！',
                            operator=loginuser, operator_display=get_object_or_404(users, username=loginuser).display, )
        mglogobj.save()
        transaction.commit()
        title_prefix = "编码同步提醒"
        _mail(request, mogoobj.id, title_prefix, loginuser, mogoobj.mogo_target, '', mogoobj.mogo_stat)
        context = {'status': '提交成功！'}
    except Exception as msg:
        transaction.rollback()
        logger.error(traceback.format_exc())
        context = {'status': '提交失败！'}
    return JsonResponse(context)


# 同步mongo编码
@csrf_exempt
def mongosync(request):
    if request.method == 'POST':
        loginuser = request.session.get('login_username', False)
        mg_name = str(request.POST.get('mg_name', False)).strip()
        mg_id = int(request.POST.get('mg_id', False))
        mgobj = get_object_or_404(mogocode, pk=mg_id, mogo_name=mg_name)
        s_env = mgobj.mogo_source
        t_env = mgobj.mogo_target
        c_type = mgobj.mogo_type

        c_url = request.POST.get(('c_url').strip(), False)

        s_list = SyncSc(mg_name, c_type, s_env, t_env, c_url).s_code()
        # s_list = mg_sync.s_code()
        mgdict = {}
        mgdict['mgid'] = mg_id
        mgdict['mgname'] = mg_name

        if s_list == "inuse":
            context = {'mgdict': "inuse"}

        elif s_list == "notexist":
            context = {'mgdict': "notexist"}

        elif isinstance(s_list, object):
            mgdict['s_list'] = s_list
            t_list = SyncSc(mg_name, c_type, s_env, t_env, c_url).t_code()
            transaction.set_autocommit(False)
            try:
                oper_desc = '执行同步'
                if t_list in Const.mogostat.values():
                    mgdict['t_list'] = t_list
                    mgobj.mogo_stat = t_list
                    mgobj.mogo_audit = users.objects.get(username=loginuser)
                    mgobj.mogo_fintime = getNow()
                    mgobj.save()
                    oper_info = '操作结果 ：' + t_list

                elif isinstance(t_list, object):
                    mgdict['t_list'] = t_list
                    oper_info = mgdict['t_list']

                else:
                    mgdict['t_list'] = "目标环境没有sysInfo!"
                    oper_info = mgdict['t_list']

                mglogobj = mongolog(audit_id=mgobj, operation_type=1, operation_type_desc=oper_desc,
                                    operation_info=oper_info, operator=loginuser,
                                    operator_display=get_object_or_404(users, username=loginuser).display, )
                mglogobj.save()
                transaction.commit()

                title_prefix = ""
                if c_url and c_type == 0:
                    title_prefix = "接口同步完毕"
                elif not c_url and c_type == 1:
                    title_prefix = "定时器同步完毕"
                elif not c_url and c_type == 2:
                    title_prefix = "MQ同步完毕"
                else:
                    pass
                _mail(request, mgobj.id, title_prefix, loginuser, mgobj.mogo_target, '', mgobj.mogo_stat)

                context = {'mgdict': mgdict}

            except Exception as msg:
                transaction.rollback()
                logger.error(traceback.format_exc())
                context = {'errMsg': msg}
                return render(request, 'error.html', context)
        else:
            context = {'mgdict': mgdict}
        return JsonResponse(context)


@csrf_exempt
def mongoabort(request):
    if request.method == 'POST':
        loginuser = request.session.get('login_username', False)
        mg_name = str(request.POST.get('mg_name', False)).strip()
        mg_id = int(request.POST.get('mg_id', False))
        transaction.set_autocommit(False)
        try:
            mgobj = get_object_or_404(mogocode, pk=mg_id, mogo_name=mg_name)
            mgobj.mogo_stat = Const.mogostat['abort']
            mgobj.mogo_fintime = getNow()
            mgobj.mogo_audit = users.objects.get(username=loginuser)
            mgobj.save()
            mglogobj = mongolog(audit_id=mgobj, operation_type=2, operation_type_desc='终止工单',
                                operation_info='操作人员将工单终止！', operator=loginuser,
                                operator_display=get_object_or_404(users, username=loginuser).display, )
            mglogobj.save()
            transaction.commit()
            title_prefix = "接口同步终止"
            _mail(request, mgobj.id, title_prefix, loginuser, mgobj.mogo_target, '', mgobj.mogo_stat)
            context = {"status": "已终止"}
        except Exception as e:
            logger.error(traceback.format_exc())
            transaction.rollback()
            context = {"status": str(e)}
        return JsonResponse(context)


@csrf_exempt
def codesearch(request):
    if request.method == 'POST':
        loginuser = request.session.get('login_username', False)
        code_type = int(request.POST.get('code_type', False))
        code_name = str(request.POST.get('code_name', False)).strip()
        code_env = str(request.POST.get('code_env', False))
        code_list = SyncSc(code_name, code_type, code_env, '', '').find_code()
        all_sources = []
        if code_list:
            for x in code_list:
                print(x)
                if 'service' in x and x['service']:
                    all_sources.append("<br>" + str(x['service']) + "<br>")
                elif 'flow' in x and x['flow']:
                    all_sources.append("<br>" + str(x['flow']) + "<br>")
                elif 'flow2' in x and x['flow2']:
                    all_sources.append("<br>" + str(x['flow2']) + "<br>")
                elif 'resource' in x and x['resource']:
                    all_sources.append("<br>" + str(x['resource']) + "<br>")
                elif 'sysinfo' in x and x['sysinfo']:
                    all_sources.append("<br>" + str(x['sysinfo']) + "<br>")
                elif 'tssTimer' in x and x['tssTimer']:
                    all_sources.append("<br>" + str(x['tssTimer']) + "<br>")
                elif 'mQQueue' in x and x['mQQueue']:
                    all_sources.append("<br>" + str(x['mQQueue']) + "<br>")
                else:
                    pass
            else:
                pass
        context = {"all_sources": all_sources}
        return JsonResponse(context)


# 获取工单日志
@csrf_exempt
def log(request):
    mogo_id = int(request.POST.get('mogo_id', False))
    mogo_name = request.POST.get('mogo_name', False)
    audit_id = mogocode.objects.get(pk=mogo_id, mogo_name=mogo_name)
    mogo_logs = mongolog.objects.filter(audit_id=audit_id).order_by('-id').values(
        'operation_type_desc',
        'operation_info',
        'operator_display',
        'operation_time')
    count = mongolog.objects.filter(audit_id=audit_id).count()

    # QuerySet 序列化
    rows = [row for row in mogo_logs]
    result = {"total": count, "rows": rows}

    return JsonResponse(result)


@csrf_exempt
def mgmutifilter(request):
    mogo_source = request.POST.get('sourceenv', False)
    start_time = request.POST.get('s_time', False)
    end_time = request.POST.get('e_time', False)
    loginuser = request.session.get('login_username', False)
    if start_time:
        start_time = str(start_time).strip()
    elif end_time:
        end_time = str(end_time).strip()
    else:
        pass
    userobj = users.objects.get(username=loginuser)
    if userobj.role == '审核人' and userobj.is_active == 1:
        mogo_result = mogocode.objects.filter(mogo_target=mogo_source, mogo_subtime__gt=start_time,
                                              mogo_subtime__lt=end_time).order_by('-id').values(
            'id',
            'mogo_name',
            'mogo_type',
            'mogo_submit',
            'mogo_subtime',
            'mogo_fintime',
            'mogo_target',
            'mogo_stat'
        )
        count = mogocode.objects.filter(mogo_target=mogo_source, mogo_subtime__gt=start_time,
                                        mogo_subtime__lt=end_time).count()
    else:
        mogo_result = mogocode.objects.filter(mogo_target=mogo_source, mogo_subtime__gt=start_time,
                                              mogo_subtime__lt=end_time, mogo_submit=loginuser).order_by('-id').values(
            'id',
            'mogo_name',
            'mogo_type',
            'mogo_submit',
            'mogo_subtime',
            'mogo_fintime',
            'mogo_target',
            'mogo_stat'
        )
        count = mogocode.objects.filter(mogo_target=mogo_source, mogo_subtime__gt=start_time,
                                        mogo_subtime__lt=end_time, mogo_submit=loginuser).count()
    mogo_result = list(mogo_result)
    result = {"count": count, "mogo_result": mogo_result}
    return JsonResponse(result)


@csrf_exempt
def mgmuti(request):
    mogo_target = request.POST.get('mogo_target', False)
    mogo_source = request.POST.get('mogo_source', False)
    mogo_codes = json.loads(request.POST.get('mogo_codes', False))
    loginuser = request.session.get('login_username', False)

    review_dba = 'kxtxdba'
    reviewer_obj = users.objects.get(username=review_dba)

    mglog_auditid = {}
    transaction.set_autocommit(False)
    try:
        mogo_list = [mogocode(mogo_name=i, mogo_type=mogo_codes[i], mogo_submit=loginuser, mogo_audit=reviewer_obj,
                              mogo_stat=Const.mogostat['waiting'], mogo_subtime=getNow(), mogo_source=mogo_source,
                              mogo_target=mogo_target) for i in mogo_codes]
        mogocode.objects.bulk_create(mogo_list)

        for i, k in mogo_codes.items():
            mogocode_id = mogocode.objects.get(mogo_name=i, mogo_type=k, mogo_submit=loginuser, mogo_audit=reviewer_obj,
                                               mogo_stat=Const.mogostat['waiting'], mogo_source=mogo_source,
                                               mogo_target=mogo_target)
            print(mogocode_id)
            try:
                mglogobj = mongolog.objects.get(audit_id=mogocode_id, operation_type=0, operation_type_desc='提交工单',
                                                operation_info='等待操作人员处理！',
                                                operator=loginuser,
                                                operator_display=get_object_or_404(users, username=loginuser).display, )
                print(mglogobj)
            except Exception:
                mglog_auditid[i] = mogocode_id

        mglog_list = [mongolog(audit_id=mglog_auditid[i], operation_type=0, operation_type_desc='提交工单',
                               operation_info='等待操作人员处理！',
                               operator=loginuser,
                               operator_display=get_object_or_404(users, username=loginuser).display, ) for i in
                      mglog_auditid]
        mongolog.objects.bulk_create(mglog_list)
        transaction.commit()
        context = {'status': '提交成功！'}
    except Exception as msg:
        transaction.rollback()
        logger.error(traceback.format_exc())
        context = {'status': '提交失败！'}

    return JsonResponse(context)


# SQL工单跳过inception执行回调
def execute_skip_inception(workflowId, instance_name, db_name, sql_content, url):
    workflowDetail = workflow.objects.get(id=workflowId)
    try:
        # 执行sql
        t_start = time.time()
        execute_result = Dao(instance_name=instance_name).mysql_execute(db_name, sql_content)
        t_end = time.time()
        execute_time = "%5s" % "{:.4f}".format(t_end - t_start)
        execute_result['execute_time'] = execute_time + 'sec'

        workflowDetail = workflow.objects.get(id=workflowId)
        if execute_result.get('Warning'):
            workflowDetail.status = Const.workflowStatus['exception']
        elif execute_result.get('Error'):
            workflowDetail.status = Const.workflowStatus['exception']
        else:
            workflowDetail.status = Const.workflowStatus['finish']
        workflowDetail.finish_time = getNow()
        # workflowDetail.review_content =
        workflowDetail.execute_result = json.dumps(execute_result)
        workflowDetail.is_manual = 1
        workflowDetail.audit_remark = ''
        workflowDetail.is_backup = '否'
        # 关闭后重新获取连接，防止超时
        connection.close()
        workflowDetail.save()
    except Exception:
        logger.error(traceback.format_exc())

        # 发送消息
        # _mail(request, rel_version, title_prefix, engineer, deploy_env, release_name, execute_status)
