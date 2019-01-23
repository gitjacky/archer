# -*- coding: UTF-8 -*- 
from django.db import models
from django.contrib.auth.models import AbstractUser
from .aes_decryptor import Prpcrypt

# Create your models here.

#角色分两种：
#1.工程师：可以提交SQL上线单的工程师们，username字段为登录用户名，display字段为展示的中文名。
#2.审核人：可以审核并执行SQL上线单的管理者、高级工程师、系统管理员们。
class users(AbstractUser):
    display = models.CharField('显示的中文名', max_length=50,null=False)
    role = models.CharField('角色', max_length=20, choices=(('工程师','工程师'),('审核人','审核人')), default='工程师')
    
    def getgroup(self):
        return ",".join([str(p) for p in self.groups.all()])
    getgroup.short_description = "用户组"
    group_name = property(getgroup)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = u'用户配置'
        verbose_name_plural = u'用户配置'

# 配置信息表
class config(models.Model):
    item = models.CharField('配置项', max_length=50, primary_key=True)
    value = models.CharField('配置项值', max_length=200)
    description = models.CharField('描述', max_length=200, default='', blank=True)

    class Meta:
        managed = True
        db_table = 'sql_config'
        verbose_name = u'系统配置'
        verbose_name_plural = u'系统配置'

#各个线上主库地址。
class master_config(models.Model):
    cluster_name = models.CharField('环境名称', max_length=50)
    master_host = models.CharField('数据库地址', max_length=200)
    master_port = models.IntegerField('端口', default=3306)
    master_user = models.CharField('登录用户名', max_length=100)
    master_password = models.CharField('登录密码', max_length=300)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.cluster_name
    class Meta:
        verbose_name = u'主库地址'
        verbose_name_plural = u'主库地址'

    def save(self, *args, **kwargs):
        pc = Prpcrypt() #初始化
        self.master_password = pc.encrypt(self.master_password)
        super(master_config, self).save(*args, **kwargs)


#存放各个SQL上线工单的详细内容，可定期归档或清理历史数据，也可通过alter table workflow row_format=compressed; 来进行压缩
class workflow(models.Model):
    workflow_name = models.CharField('工单内容', max_length=50)
    engineer = models.CharField('发起人', max_length=50)
    review_man = models.CharField('审核人', max_length=50)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    finish_time = models.DateTimeField('结束时间', null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('已正常结束','已正常结束'),('人工终止流程','人工终止流程'),('自动审核中','自动审核中'),('等待DBA审核','等待DBA审核'),('执行中','执行中'),('自动审核不通过','自审核不通过'),('执行有异常','执行有异常')))
    #is_backup = models.IntegerField('是否备份，0为否，1为是', choices=((0,0),(1,1)))
    is_backup = models.CharField('是否备份', choices=(('否','否'),('是','是')), max_length=20)
    review_content = models.TextField('自动审核内容的JSON格式')
    cluster_name = models.CharField('环境名称', max_length=50)     #master_config表的cluster_name列的外键
    reviewok_time = models.DateTimeField('人工审核通过的时间', null=True, blank=True)
    sql_content = models.TextField('具体sql内容')
    execute_result = models.TextField('执行结果的JSON格式')
    is_manual = models.IntegerField('是否跳过inception', choices=((0, '否'), (1, '是')), default=0)


    def __str__(self):
        return self.workflow_name
    class Meta:
        verbose_name = u'工单管理'
        verbose_name_plural = u'工单管理'
        permissions = {
            ('can_select_workflow',u'工单查询权限'),
            ('can_execute_workflow',u'工单执行权限'),
            ('can_cancel_workflow', u'工单中止权限'),
        }

#存放各个版本发布的版本信息。
class workrelease(models.Model):
    release_name = models.CharField(verbose_name='版本名称',max_length=60)
    release_path = models.CharField(verbose_name='svn路径',max_length=70)
    deploy_env = models.CharField(verbose_name='发布环境',max_length=50)
    submit_user = models.CharField(verbose_name='SQL提交人',max_length=20)
    audit_user = models.ForeignKey(users,verbose_name='审核人')
    submit_time = models.DateTimeField(verbose_name='提交时间',auto_now_add=True)
    # release_status = models.CharField(verbose_name='DBA审核状态', max_length=60)
    execute_status = models.CharField(verbose_name='版本执行状态',max_length=50, choices=(('已正常结束','已正常结束'),('人工终止流程','人工终止流程'),('自动审核中','自动审核中'),('等待DBA审核','等待DBA审核'),('执行中','执行中'),('自动审核不通过','自审核不通过'),('执行有异常','执行有异常')))

    def __str__(self):
        return self.release_name
    class Meta:
        verbose_name = u'版本SQL工单'
        verbose_name_plural = u'版本SQL工单'
        permissions = {
            ('can_select_workrelease',u'查询版本工单权限')
        }

class detailrecords(models.Model):
    engineer = models.CharField(verbose_name='发起人', max_length=50)
    review_man = models.CharField(verbose_name='审核人', max_length=50)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    finish_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    status = models.CharField(max_length=50, choices=(('已正常结束','已正常结束'),('人工终止流程','人工终止流程'),('自动审核中','自动审核中'),('等待DBA审核','等待DBA审核'),('执行中','执行中'),('自动审核不通过','自审核不通过'),('执行有异常','执行有异常')))
    release_version = models.ForeignKey(workrelease,verbose_name='版本号信息',on_delete=models.CASCADE)
    release_file = models.CharField(verbose_name='版本SQL文件', max_length=100)
    review_content = models.TextField(verbose_name='自动审核内容的JSON格式')
    cluster_name = models.CharField(verbose_name='环境名称', max_length=50)     #master_config表的cluster_name列的外键
    reviewok_time = models.DateTimeField(verbose_name='人工审核通过的时间', null=True, blank=True)
    sql_content = models.TextField(verbose_name='具体sql内容')
    is_backup = models.CharField('是否备份', choices=(('否','否'),('是','是')), max_length=20)
    execute_result = models.TextField(verbose_name='执行结果的JSON格式')

    def __str__(self):
        return str(self.release_version)

    class Meta:
        verbose_name = u'版本SQL文件'
        verbose_name_plural = u'版本SQL文件'
        permissions = {
            ('can_select_detailrecords',u'查询详情权限')
        }

class rel_memo(models.Model):
    rel_id = models.OneToOneField(workrelease,verbose_name='版本号信息',on_delete=models.CASCADE)
    memo = models.TextField(verbose_name='开发备注信息',max_length=200,default='')
    dba_memo = models.TextField(verbose_name='DBA备注信息',max_length=200,default='')

    def __str__(self):
        return str(self.rel_id)

    class Meta:
        verbose_name = u'版本SQL备注'
        verbose_name_plural = u'版本SQL备注'
        permissions = {
            ('can_select_relmemo',u'查询备注权限'),
            ('can_change_devmemo', u'修改开发备注权限'),
            ('can_change_dbamemo', u'修改dba备注权限'),
        }

class mogocode(models.Model):
    mogo_name = models.CharField(verbose_name='编码名称', max_length=30)
    mogo_type = models.IntegerField('编码类型', choices=((0,'服务接口'),(1,'定时器'),(2,'MQ队列')))
    mogo_submit = models.CharField(verbose_name='提交人',max_length=25)
    mogo_audit = models.ForeignKey(users,verbose_name='审核人')
    mogo_stat = models.CharField(verbose_name='状态',max_length=20)
    mogo_subtime = models.DateTimeField(verbose_name='提交时间', auto_now_add=True)
    mogo_fintime = models.DateTimeField(verbose_name='结束时间', null=True)
    mogo_source = models.CharField(verbose_name='源环境名',max_length=30)
    mogo_target = models.CharField(verbose_name='目的环境', max_length=30)

    def __str__(self):
        return self.mogo_name

    class Meta:
        verbose_name = u'MONGO编码'
        verbose_name_plural = u'MONGO编码'

        permissions = {
            ('can_select_mogocode', u'查询接口权限'),
            ('can_sync_mogocode', u'同步接口权限'),
            ('can_cancel_mogocode', u'中止接口权限'),
        }

#mongodb主库地址。
class mongo_config(models.Model):
    db_name = models.CharField('环境名称', max_length=50)
    mongo_host = models.CharField('数据库地址', max_length=200)
    mongo_port = models.IntegerField('端口', default=27017)
    mongo_user = models.CharField('登录用户名', max_length=100)
    mongo_password = models.CharField('登录密码', max_length=300)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.db_name
    class Meta:
        verbose_name = u'MONGO库信息'
        verbose_name_plural = u'MONGO库信息'

    def save(self, *args, **kwargs):
        pc = Prpcrypt() #初始化
        self.mongo_password = pc.encrypt(self.mongo_password)
        super(mongo_config, self).save(*args, **kwargs)

# Mongo同步日志表
class mongolog(models.Model):
    id = models.AutoField(primary_key=True)
    audit_id = models.ForeignKey(mogocode, verbose_name='工单审批id', db_index=True)
    operation_type = models.SmallIntegerField('操作类型，0提交/待审核、1执行成功、2人工终止、3执行失败')
    operation_type_desc = models.CharField('操作类型描述', max_length=10)
    operation_info = models.CharField('操作信息', max_length=200)
    operator = models.CharField('操作人', max_length=30)
    operator_display = models.CharField('操作人中文名', max_length=50, default='')
    operation_time = models.DateTimeField(auto_now_add=True)

    def __int__(self):
        return self.audit_id

    class Meta:
        verbose_name = u'mongo同步日志表'
        verbose_name_plural = u'mongo同步日志表'

