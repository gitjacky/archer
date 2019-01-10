# -*- coding: UTF-8 -*-
import logging
import traceback

import simplejson as json
from django.http import HttpResponse

from .models import config
from django.db import transaction
from django.core.cache import cache

logger = logging.getLogger('default')


class SysConfig(object):
    def __init__(self):
        if cache.get('sys_config'):
            self.sys_config = cache.get('sys_config')
        else:
            try:
                # 获取系统配置信息
                all_config = config.objects.all().values('item', 'value')
                sys_config = {}
                for items in all_config:
                    if items['value'] == 'true':
                        items['value'] = True
                    elif items['value'] == 'false':
                        items['value'] = False
                    else:
                        pass
                    sys_config[items['item']] = items['value']
                self.sys_config = sys_config
                # 增加缓存
                cache.add('sys_config', self.sys_config, timeout=None)
            except Exception:
                self.sys_config = {}