from datetime import datetime

from django.db import models

# Create your models here.
#用户模型
class User(models.Model):
    #主键
    id = models.AutoField(primary_key = True)
    #账号
    username = models.CharField(max_length=20)
    #密码：
    password = models.CharField(max_length=100)
    #盐
    salt = models.CharField(max_length=4)
    #姓名
    truename = models.CharField(max_length=20,null=True)
    #邮箱
    email = models.CharField(max_length=30,null=True)
    #手机号
    phone = models.CharField(max_length=20, null=True)
    #状态  0 未审核  1 审核通过 -1 黑名单
    state = models.IntegerField(default=0)
    #是否可用  0 不可用 1 可用
    isValid = models.IntegerField(db_column='is_valid',default=1)
    #创建时间
    createDate = models.DateTimeField(db_column='create_date',default=datetime.now())
    #修改时间
    updateDate = models.DateTimeField(db_column='update_date',null=True)

    #元信息
    class Meta(object):
        db_table = 't_user'


class ModelManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(isValid=1)

#资源表
class Module(models.Model):
    #资源名称
    moduleName = models.CharField(max_length=50, db_column='module_name')
    #样式
    moduleStyle = models.CharField(max_length=120, db_column='module_style')
    #跳转地址
    url = models.CharField(max_length=100, db_column='url')
    #自关联
    parent = models.ForeignKey('self', db_column='parent_id',db_constraint=False,on_delete=models.DO_NOTHING,default=-1)
    #父级操作
    parentOptValue = models.CharField(max_length=20,db_column='parent_opt_value')
    #级别
    grade = models.IntegerField(db_column='grade')
    #操作值
    optValue = models.CharField(max_length=20,db_column='opt_value')
    #排序顺序
    orders = models.IntegerField(db_column='orders')
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',auto_now_add=True)
    updateDate = models.DateTimeField(max_length=20, db_column='update_date', auto_now_add=True)

    objects = ModelManager()

    class Meta(object):
        db_table = 't_module'
    pass