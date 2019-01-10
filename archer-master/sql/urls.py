# -*- coding: UTF-8 -*-
from django.conf.urls import url,include
from . import views, views_ajax

urlpatterns = [
    url(r'^$', views.allworkflow, name='allworkflow'),
    url(r'^index/$', views.allworkflow, name='allworkflow'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^submitsql/$', views.submitsql, name='submitsql'),
    url(r'editsql/$', views.submitsql, name='editsql'),
    url(r'^allworkflow/$', views.allworkflow, name='allworkflow'),
    url(r'^detail/(?P<workflowId>[0-9]+)/$', views.detail, name='detail'),
    url(r'^autoreview/$', views.autoreview, name='autoreview'),
    url(r'^execute/$', views.execute, name='execute'),
    url(r'^cancel/$', views.cancel, name='cancel'),
    url(r'^rollback/$', views.rollback, name='rollback'),
    url(r'^dbaprinciples/$', views.dbaprinciples, name='dbaprinciples'),
    url(r'^charts/$', views.charts, name='charts'),

    url(r'^authenticate/$', views_ajax.authenticateEntry, name='authenticate'),
    url(r'^simplecheck/$', views_ajax.simplecheck, name='simplecheck'),
    url(r'^getMonthCharts/$', views_ajax.getMonthCharts, name='getMonthCharts'),
    url(r'^getPersonCharts/$', views_ajax.getPersonCharts, name='getPersonCharts'),
    url(r'^getCancelCharts/$', views_ajax.getCancelCharts, name='getCancelCharts'),
    url(r'^getOscPercent/$', views_ajax.getOscPercent, name='getOscPercent'),
    url(r'^getWorkflowStatus/$', views_ajax.getWorkflowStatus, name='getWorkflowStatus'),
    url(r'^stopOscProgress/$', views_ajax.stopOscProgress, name='stopOscProgress'),

    url(r'^versions/', views_ajax.versionsql, name='versions'),  # jacky
    url(r'^search/$', views.searchflow, name='searchflow'),  #jacky
    url(r'^versioninfo/', views_ajax.versioninfo, name='versioninfo'), #jacky
    url(r'^clusterandaudit/', views_ajax.clustersandAudit, name='clustersandAudit'), #jacky

    url(r'^allrelease/', views_ajax.allrelease, name='allrelease'), #jacky
    url(r'^relsdetail/(?P<relsid>[0-9]+)/$', views.relsdetail, name='relsdetail'), #jacky
    url(r'^relfilter/', views_ajax.relfilter, name='relfilter'),  # jacky
    url(r'^relautoreview/', views_ajax.relautoreview, name='relautoreview'), #jacky
    url(r'^resdetail/', views_ajax.resdetail, name='resdetail'), #jacky
    url(r'^dbamemo/', views_ajax.getmemo, name='getmemo'), #jacky
    url(r'^memosave/', views_ajax.memosave, name='memosave'), #jacky
    url(r'^relsexecute/', views_ajax.relsexecute, name='relsexecute'), #jacky
    url(r'^getrelstatus/', views_ajax.getrelstatus, name='getrelstatus'), #jacky
    url(r'^relstop/', views_ajax.relstop, name='relstop'), #jacky
    url(r'^getrelinfo/', views_ajax.getrelinfo, name='getrelinfo'),  # jacky
    url(r'^relother/', views_ajax.relother, name='relother'),  # jacky

    url(r'^ddlcount/', views.ddlcount, name='ddlcount'),  # jacky
    url(r'^ddlajx/', views_ajax.ddlajx, name='ddlajx'),  # jacky

    url(r'^mongo/', views.mongowork, name='mongo'),  # jacky
    url(r'^mongolog/', views_ajax.log, name='mongolog'),  # jacky
    url(r'^mgadd/', views_ajax.mgadd, name='mgadd'),  # jacky
    url(r'^mgcommit/', views_ajax.mgcommit, name='mgcommit'),  # jacky
    url(r'^mongosync/', views_ajax.mongosync, name='mongosync'),  # jacky
    url(r'^mongoabort/', views_ajax.mongoabort, name='mongoabort'),  # jacky
    url(r'^mgcode/', views.mgcode, name='mgcode'),  # jacky
    url(r'^codesearch/', views_ajax.codesearch, name='codesearch'),  # jacky
    url(r'^mgfind/', views.mgfind, name='mgfind'),  # jacky
    url(r'^mgmutisubmit/', views.mgmutisubmit, name='mgmutisubmit'),  # jacky
    url(r'^mgmutifilter/', views_ajax.mgmutifilter, name='mgmutifilter'),  # jacky
    url(r'^mgmulti/$', views_ajax.mgmuti, name='mgmuti'),  # jacky

    url(r'^sqlquery/', views.sqlquery, name='sqlquery'),  # jacky
    url(r'^config/', views.parameter_config, name='parameter_config'),  # jacky

]
