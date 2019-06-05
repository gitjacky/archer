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
    {'key': 'group', 'name': '对象关联管理', 'url': '/group/', 'class': 'glyphicon glyphicon-user'},
    {'key': 'instance', 'name': '实例配置管理', 'url': '/instance/', 'class': 'glyphicon glyphicon-th-large'},
    {'key': 'config', 'name': '参数配置管理', 'url': '/config/', 'class': 'glyphicon glyphicon-globe'},
)
leftMenuDoc = (
    {'key': 'charts', 'name': '统计图表展示', 'url': '/charts/', 'class': 'glyphicon glyphicon-stats'},
    {'key': 'dbaprinciples', 'name': 'SQL审核必读', 'url': '/dbaprinciples/', 'class': 'glyphicon glyphicon-book'},
)
# Jacky
leftMenuDba = (
    {'key': 'ddlcount', 'name': '开发DDL统计', 'url': '/ddlcount/', 'class': 'glyphicon glyphicon-list-alt'},
    {'key': 'archsync', 'name': '实例结构对比', 'url': '/archsync/', 'class': 'glyphicon glyphicon-retweet'},

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
