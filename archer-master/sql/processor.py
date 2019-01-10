# -*- coding: UTF-8 -*- 
from .models import users

leftMenuCommon = (
    {'key': 'allworkflow', 'name': '开发SQL审核', 'url': '/allworkflow/', 'class': 'glyphicon glyphicon-home'},
    {'key': 'versions', 'name': '版本SQL上线', 'url': '/versions/', 'class': 'glyphicon glyphicon-cloud-upload'},
    {'key': 'mongo', 'name': 'MONGO同步', 'url': '/mongo/', 'class': 'glyphicon glyphicon-leaf'},
    {'key': 'dbaprinciples', 'name': 'SQL审核必读', 'url': '/dbaprinciples/', 'class': 'glyphicon glyphicon-book'},
)
leftMenuQuery = (
    {'key': 'mysqlquery', 'name': 'MySQL查询', 'url': '/sqlquery/', 'class': 'glyphicon glyphicon-search'},
)
leftMenuSuper = (
    {'key': 'masterconfig', 'name': '主库地址配置', 'url': '/admin/sql/master_config/', 'class': 'glyphicon glyphicon-user'},
    {'key': 'userconfig', 'name': '用户权限配置', 'url': '/admin/sql/users/', 'class': 'glyphicon glyphicon-th-large'},
    {'key': 'workflowconfig', 'name': '所有工单管理', 'url': '/admin/sql/workflow/', 'class': 'glyphicon glyphicon-list-alt'},
)
leftMenuDoc = (

    {'key': 'charts', 'name': '统计图表展示', 'url': '/charts/', 'class': 'glyphicon glyphicon-stats'},
)
# Jacky
leftMenuDba = (
    {'key': 'workflowconfig', 'name': '后台数据管理', 'url': '/admin/sql/', 'class': 'glyphicon glyphicon-menu-hamburger'},
    {'key': 'ddlcount', 'name': '开发DDL统计', 'url': '/ddlcount/', 'class': 'glyphicon glyphicon-list-alt'},
    {'key': 'config', 'name': '参数配置管理', 'url': '/config/', 'class': 'glyphicon glyphicon-globe'},

)


def global_info(request):
    """存放用户，会话信息等."""
    loginUser = request.session.get('login_username', None)
    if loginUser is not None:
        user = users.objects.get(username=loginUser)
        if user.is_superuser:
            leftMenuBtns = leftMenuCommon + leftMenuQuery + leftMenuSuper + leftMenuDba + leftMenuDoc
        elif user.has_perm('sql.can_select_mogocode'):
            leftMenuBtns = leftMenuCommon + leftMenuQuery + leftMenuDba + leftMenuDoc
        else:
            leftMenuBtns = leftMenuCommon + leftMenuDoc
    else:
        leftMenuBtns = ()

    return {
        'loginUser': loginUser,
        'leftMenuBtns': leftMenuBtns,
    }
