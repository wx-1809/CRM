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


