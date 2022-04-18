#coding='utf-8'
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class URLMiddleware(MiddlewareMixin):
    """URL 访问过滤中间件"""
    def process_request(self,request):
        #允许访问的地址
        urls = ['registry', 'login', 'unique_username','captcha']
        url = request.path.split('/')[1] #e.g. login
        #如果访问路径不存在，判断session中是否有用户信息，有则放行
        if url not in urls:
            user = request.session.get('user')
            #没有则重定向到 login页面
            if not user:
                return redirect('system:login')

