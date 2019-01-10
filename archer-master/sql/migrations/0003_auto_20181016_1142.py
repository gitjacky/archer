# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0002_mongolog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mongolog',
            name='operation_type',
            field=models.SmallIntegerField(verbose_name='操作类型，0提交/待审核、1执行成功、2人工终止、3执行失败'),
        ),
    ]
