# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='mongolog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('operation_type', models.SmallIntegerField(verbose_name='操作类型，0提交/待审核、1执行成功、2执行失败')),
                ('operation_type_desc', models.CharField(max_length=10, verbose_name='操作类型描述')),
                ('operation_info', models.CharField(max_length=200, verbose_name='操作信息')),
                ('operator', models.CharField(max_length=30, verbose_name='操作人')),
                ('operator_display', models.CharField(max_length=50, verbose_name='操作人中文名', default='')),
                ('operation_time', models.DateTimeField(auto_now_add=True)),
                ('audit_id', models.ForeignKey(to='sql.mogocode', verbose_name='工单审批id')),
            ],
            options={
                'verbose_name': 'mongo同步日志表',
                'verbose_name_plural': 'mongo同步日志表',
            },
        ),
    ]
