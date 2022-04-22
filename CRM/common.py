#coding='utf-8'
# from django.contrib.messages.storage.base import Message
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.clickjacking import xframe_options_exempt

from system.models import User, Permission, Module


class URLMiddleware(MiddlewareMixin):
    """URL 访问过滤中间件"""
    def process_request(self, request):
        #允许访问的地址
        urls = ['registry', 'login', 'unique_username','captcha']
        #print(request.path)
        url = request.path.split('/')[1] #e.g. login
        #如果访问路径不存在，判断session中是否有用户信息，有则放行
        if url not in urls:
            user = request.session.get('user')
            #没有则重定向到 login页面
            if not user:
                return redirect('system:login')
            #有则放行，并查询该用户权限存入session
            try:
                #删除该用户的权限信息
                del request.session['user_permission']
                # pass
            except Exception as e:
                pass

            #根据ID获取用户
            u = User.objects.get(id=user['id'])
            #获取用户的所有角色ID
            role_id = u.roles.values_list('id',flat=True).all()
            #根据角色ID查询模块ID
            module_id = Permission.objects.values_list('module',flat=True).filter(role__id__in=role_id)
            #根据模块ID查询获取资源权限值
            opt_value = list(Module.objects.values_list('optValue',flat=True).filter(pk__in=module_id))
            #根据用户将权限值添加至session
            request.session['user_permission']=opt_value

class CustomSystemException(Exception):
    """自定义异常类"""
    def __init__(self, code=400,msg='系统错误，请联系管理员'):
        self.code = code
        self.msg = msg

    @staticmethod
    def eroor(msg):
        c = CustomSystemException(msg = msg)
        return c

class ExceptionMiddleware(MiddlewareMixin):
    """全局异常处理中间件"""

    @xframe_options_exempt
    def process_exception(self,request,excepiton):
        #如果是自定义异常
        if isinstance(excepiton, CustomSystemException):
            result = Message(code=excepiton.code, msg=excepiton.msg).result()
        elif isinstance(excepiton,Exception) or isinstance(excepiton,BaseException):
            #如果是python系统异常
            #系统出现异常，将异常信息存入数据库或者是日志记录文件，方便维护查看
            result = Message(code=400, msg='系统错误，请联系管理员').result()

        #判断请求是否是ajax
            return JsonResponse(result)
        else:
            return  render(request,'404.html',result)

class Message(object):
    """公共返回对象"""

    def __init__(self, code=200, msg='success',obj=None):
        self.code=code,
        self.msg =msg,
        self.obj=obj

    def result(self):
        result = {'code':self.code[0],'msg':self.msg[0]}
        if self.obj:
            result['obj'] = self.obj[0]

        return result

