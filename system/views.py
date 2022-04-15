import random
import string
from hashlib import md5

from captcha.image import ImageCaptcha
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.shortcuts import render
from .models import User

# Create your views here.
#注册账号
def registry(request):
    """GET请求跳转注册页面/POST请求完成注册流程"""
    if request.method == 'GET':
        return render(request, 'registry.html')#跳转注册页面

    if request.method == 'POST':
        try:
            #接收参数
            username = request.POST.get('username')
            password = request.POST.get('password')
            code = request.POST.get('code')
            #从session中获得验证码
            session_code = request.session.get('code')
            #验证码失效返回提示信息
            if not session_code:
                return JsonResponse({'code':400,'msg':'验证码提交失败请重新获取'})
            #验证码不一致的返回提示信息
            if code.upper() != session_code.upper():
                return JsonResponse({'code':400, 'msg':'验证码输入错误'})
            #准备盐
            salt = generate_code()

            #md5+盐进行密码加密
            md5_password = md5((password+salt).encode(encoding='utf-8')).hexdigest()
            #插入数据库
            user = User(username=username, password=md5_password,salt=salt)
            user.save()
            return JsonResponse({'code':200,'msg':'注册成功，请联系管理员审核账号'})

        except Exception as e:
            return JsonResponse({'code':400,'msg':'注册失败'})



#登录账号
def login(request):
    """GET跳转登录页面/POST完成登录流程"""
    if request.method =='GET':
        #跳转登录界面
        return render(request, 'login.html')
    if request.method == 'POST':
        

        pass


@require_GET
def unique_username(request):
    """验证账号是否唯一"""
    try:
        #接收参数
        username = request.GET.get('username')
        #查询是否有该用户
        user =User.objects.get(username=username)#返回是对象
        #有用户信息
        return JsonResponse({'code':200, 'msg':'该账户已存在'})

    except User.DoesNotExist as e:
        print(e)
        #有异常信息，说明该用户不存在
        return JsonResponse({'code':200,'msg':'恭喜你，可以注册'})

#验证码编写
def generate_code(code_len=4):
    """生成字母加数字组合验证码字符串"""
    #获取所有大小写字母
    letters = string.ascii_letters
    #获取所有数字
    digits = string.digits
    #随机选取4个字符（列表生成式）
    return ''.join([random.choice(digits+letters) for i in range(4)])


@require_GET
def generate_captcha(request):
    """生成图形验证码"""
    #生成字母加数字组合验证码字符串
    code = generate_code();
    #初始化图形验证码对象
    image = ImageCaptcha()
    #生成图像验证码，将图片保存到内存中
    captcha = image.generate(code)
    #将验证码保存到session
    request.session['code'] = code
    #60s失效
    request.session.set_expiry(60)
    #读取图片中的byte值并返回
    return HttpResponse(captcha.getvalue())

