#!/usr/local/bin/python3.4
# -*- coding: UTF-8 -*-
from django.http import JsonResponse
from django.shortcuts import render

# 管理员操作权限验证
def superuser_required(func):
    def wrapper(request, *args, **kw):
        # 获取用户信息，权限验证
        user = request.user

        if user.is_superuser is False:
            if request.is_ajax():
                result = {'status': 1, 'msg': '您无权操作，请联系管理员', 'data': []}
                return JsonResponse(result)
            else:
                context = {'errMsg': "您无权操作，请联系管理员"}
                return render(request, "error.html", context)

        return func(request, *args, **kw)
    print(wrapper)

    return wrapper