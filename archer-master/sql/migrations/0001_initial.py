# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import django.core.validators
import django.contrib.auth.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], verbose_name='username', max_length=30, unique=True)),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('email', models.EmailField(verbose_name='email address', blank=True, max_length=254)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('display', models.CharField(verbose_name='显示的中文名', max_length=50)),
                ('role', models.CharField(verbose_name='角色', choices=[('工程师', '工程师'), ('审核人', '审核人')], default='工程师', max_length=20)),
                ('groups', models.ManyToManyField(related_name='user_set', to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', blank=True, related_query_name='user', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', to='auth.Permission', help_text='Specific permissions for this user.', blank=True, related_query_name='user', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': '用户配置',
                'verbose_name': '用户配置',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='detailrecords',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('engineer', models.CharField(verbose_name='发起人', max_length=50)),
                ('review_man', models.CharField(verbose_name='审核人', max_length=50)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('finish_time', models.DateTimeField(verbose_name='结束时间', blank=True, null=True)),
                ('status', models.CharField(choices=[('已正常结束', '已正常结束'), ('人工终止流程', '人工终止流程'), ('自动审核中', '自动审核中'), ('等待DBA审核', '等待DBA审核'), ('执行中', '执行中'), ('自动审核不通过', '自审核不通过'), ('执行有异常', '执行有异常')], max_length=50)),
                ('release_file', models.CharField(verbose_name='版本SQL文件', max_length=100)),
                ('review_content', models.TextField(verbose_name='自动审核内容的JSON格式')),
                ('cluster_name', models.CharField(verbose_name='环境名称', max_length=50)),
                ('reviewok_time', models.DateTimeField(verbose_name='人工审核通过的时间', blank=True, null=True)),
                ('sql_content', models.TextField(verbose_name='具体sql内容')),
                ('is_backup', models.CharField(verbose_name='是否备份', choices=[('否', '否'), ('是', '是')], max_length=20)),
                ('execute_result', models.TextField(verbose_name='执行结果的JSON格式')),
            ],
            options={
                'verbose_name_plural': '版本SQL文件',
                'verbose_name': '版本SQL文件',
                'permissions': set([('can_select_detailrecords', '查询权限')]),
            },
        ),
        migrations.CreateModel(
            name='master_config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cluster_name', models.CharField(verbose_name='环境名称', max_length=50)),
                ('master_host', models.CharField(verbose_name='数据库地址', max_length=200)),
                ('master_port', models.IntegerField(verbose_name='端口', default=3306)),
                ('master_user', models.CharField(verbose_name='登录用户名', max_length=100)),
                ('master_password', models.CharField(verbose_name='登录密码', max_length=300)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
            ],
            options={
                'verbose_name_plural': '主库地址',
                'verbose_name': '主库地址',
            },
        ),
        migrations.CreateModel(
            name='mogocode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mogo_name', models.CharField(verbose_name='编码名称', max_length=30)),
                ('mogo_type', models.IntegerField(verbose_name='编码类型', choices=[(0, '服务接口'), (1, '定时器'), (2, 'MQ队列')])),
                ('mogo_submit', models.CharField(verbose_name='提交人', max_length=25)),
                ('mogo_stat', models.CharField(verbose_name='状态', max_length=20)),
                ('mogo_subtime', models.DateTimeField(verbose_name='提交时间', auto_now_add=True)),
                ('mogo_fintime', models.DateTimeField(verbose_name='结束时间', null=True)),
                ('mogo_source', models.CharField(verbose_name='源环境名', max_length=30)),
                ('mogo_target', models.CharField(verbose_name='目的环境', max_length=30)),
                ('mogo_audit', models.ForeignKey(verbose_name='审核人', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'MONGO编码',
                'verbose_name': 'MONGO编码',
                'permissions': set([('can_select_mogocode', '查询权限')]),
            },
        ),
        migrations.CreateModel(
            name='mongo_config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('db_name', models.CharField(verbose_name='环境名称', max_length=50)),
                ('mongo_host', models.CharField(verbose_name='数据库地址', max_length=200)),
                ('mongo_port', models.IntegerField(verbose_name='端口', default=27017)),
                ('mongo_user', models.CharField(verbose_name='登录用户名', max_length=100)),
                ('mongo_password', models.CharField(verbose_name='登录密码', max_length=300)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='更新时间', auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'MONGO库信息',
                'verbose_name': 'MONGO库信息',
            },
        ),
        migrations.CreateModel(
            name='rel_memo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('memo', models.TextField(verbose_name='开发备注信息', default='', max_length=200)),
                ('dba_memo', models.TextField(verbose_name='DBA备注信息', default='', max_length=200)),
            ],
            options={
                'verbose_name_plural': '版本SQL备注',
                'verbose_name': '版本SQL备注',
                'permissions': set([('can_select_relmemo', '查询权限')]),
            },
        ),
        migrations.CreateModel(
            name='workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('workflow_name', models.CharField(verbose_name='工单内容', max_length=50)),
                ('engineer', models.CharField(verbose_name='发起人', max_length=50)),
                ('review_man', models.CharField(verbose_name='审核人', max_length=50)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('finish_time', models.DateTimeField(verbose_name='结束时间', blank=True, null=True)),
                ('status', models.CharField(choices=[('已正常结束', '已正常结束'), ('人工终止流程', '人工终止流程'), ('自动审核中', '自动审核中'), ('等待DBA审核', '等待DBA审核'), ('执行中', '执行中'), ('自动审核不通过', '自审核不通过'), ('执行有异常', '执行有异常')], max_length=50)),
                ('is_backup', models.CharField(verbose_name='是否备份', choices=[('否', '否'), ('是', '是')], max_length=20)),
                ('review_content', models.TextField(verbose_name='自动审核内容的JSON格式')),
                ('cluster_name', models.CharField(verbose_name='环境名称', max_length=50)),
                ('reviewok_time', models.DateTimeField(verbose_name='人工审核通过的时间', blank=True, null=True)),
                ('sql_content', models.TextField(verbose_name='具体sql内容')),
                ('execute_result', models.TextField(verbose_name='执行结果的JSON格式')),
            ],
            options={
                'verbose_name_plural': '工单管理',
                'verbose_name': '工单管理',
                'permissions': set([('can_select_workflow', '查询权限')]),
            },
        ),
        migrations.CreateModel(
            name='workrelease',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('release_name', models.CharField(verbose_name='版本名称', max_length=60)),
                ('release_path', models.CharField(verbose_name='svn路径', max_length=70)),
                ('deploy_env', models.CharField(verbose_name='发布环境', max_length=50)),
                ('submit_user', models.CharField(verbose_name='SQL提交人', max_length=20)),
                ('submit_time', models.DateTimeField(verbose_name='提交时间', auto_now_add=True)),
                ('execute_status', models.CharField(verbose_name='版本执行状态', choices=[('已正常结束', '已正常结束'), ('人工终止流程', '人工终止流程'), ('自动审核中', '自动审核中'), ('等待DBA审核', '等待DBA审核'), ('执行中', '执行中'), ('自动审核不通过', '自审核不通过'), ('执行有异常', '执行有异常')], max_length=50)),
                ('audit_user', models.ForeignKey(verbose_name='审核人', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': '版本SQL工单',
                'verbose_name': '版本SQL工单',
                'permissions': set([('can_select_workrelease', '查询权限')]),
            },
        ),
        migrations.AddField(
            model_name='rel_memo',
            name='rel_id',
            field=models.OneToOneField(to='sql.workrelease', verbose_name='版本号信息'),
        ),
        migrations.AddField(
            model_name='detailrecords',
            name='release_version',
            field=models.ForeignKey(verbose_name='版本号信息', to='sql.workrelease'),
        ),
    ]
