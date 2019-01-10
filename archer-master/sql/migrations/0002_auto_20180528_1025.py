# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sql', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rel_memo',
            name='dba_memo',
            field=models.TextField(verbose_name='DBA备注信息', max_length=200, default=''),
        ),
        migrations.AlterField(
            model_name='rel_memo',
            name='memo',
            field=models.TextField(verbose_name='开发备注信息', max_length=200, default=''),
        ),
    ]
