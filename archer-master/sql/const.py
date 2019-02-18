# -*- coding: UTF-8 -*- 

class Const(object):
    workflowStatus = {
        'finish': '已正常结束',
        'abort': '人工终止流程',
        'autoreviewwait': '等待开发自审',
        'autoreviewing': '自动审核中',
        'manreviewing': '等待DBA审核',
        'executing': '执行中',
        'autoreviewwarning': '自审有警告',
        'autoreviewwrong': '自审不通过',
        'exception': '执行有异常',
                     }
    mogostat = {
        'waiting': '等待处理',
        'executing': '同步中',
        'abort': '已终止',
        'finish': '已完成',
        'exception': '有异常',
        'exist': '已存在',
    }
