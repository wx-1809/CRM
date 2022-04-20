from datetime import datetime

from django.db import models

# Create your models here.

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
    parent = models.ForeignKey('self', db_column='parent_id',db_constraint=False,
                               on_delete=models.DO_NOTHING,default=-1)
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
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',auto_now_add=True) #, default=datetime.now()

    objects = ModelManager()

    class Meta(object):
        db_table = 't_module'

#角色表
class Role(models.Model):
    roleName = models.CharField(max_length=20, db_column='role_name')
    roleRemark = models.CharField(max_length=120, db_column='role_remark')
    isValid = models.IntegerField(db_column='is_valid',default=1)
    createDate = models.DateTimeField(db_column='create_date')
    updateDate = models.DateTimeField(max_length=20,db_column='update_date',auto_now_add=True)#, default=datetime.now() , default=datetime.now()
    permissions = models.ManyToManyField(Module, through='Permission', through_fields=('role','module'))

    objects = ModelManager()

    class Meta:
        db_table = 't_role'


#角色-资源中间表
class Permission(models.Model):
    role = models.ForeignKey(Role, db_column='role_id', db_constraint=False,
                             on_delete=models.DO_NOTHING)
    module = models.ForeignKey(Module,db_column='module_id',db_constraint=False,
                               on_delete=models.DO_NOTHING)
    aclValue = models.CharField(max_length=20, db_column='acl_value')
    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',auto_now_add=True)#, default=datetime.now()
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',auto_now_add=True)#, default=datetime.now()

    objects = ModelManager()

    class Meta:
        db_table = 't_permission'


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
    createDate = models.DateTimeField(db_column='create_date',auto_now_add=True)#,default=datetime.now()
    #修改时间
    updateDate = models.DateTimeField(db_column='update_date',null=True)

    roles = models.ManyToManyField(Role, through="UserRole", through_fields=('user','role'))

    objects = ModelManager()

    #元信息
    class Meta(object):
        db_table = 't_user'

#用户-角色中间表
class UserRole(models.Model):
    user = models.ForeignKey(User,db_column='user_id',
                             db_constraint=False,on_delete=models.DO_NOTHING)
    role = models.ForeignKey(Role,db_column='role_id',
                             db_constraint=False, on_delete=models.DO_NOTHING)

    isValid = models.IntegerField(db_column='is_valid', default=1)
    createDate = models.DateTimeField(db_column='create_date',auto_now_add=True)#, default=datetime.now()
    updateDate = models.DateTimeField(max_length=20, db_column='update_date',auto_now_add=True)#, default=datetime.now()

    objects = ModelManager()

    class Meta:
        db_table = 't_user_role'

























