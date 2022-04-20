import random
import string
from datetime import datetime
from hashlib import md5

from captcha.image import ImageCaptcha
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_GET
from django.shortcuts import render, redirect
from .models import User
from .models import Module
from .models import Permission

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
        try:
            #接收参数
            username = request.POST.get('username')
            password = request.POST.get('password')
            code = request.POST.get('code')
            #从session中获取验证码
            session_code = request.session.get('code')
            # 验证码失效返回提示信息
            if not session_code:
                return JsonResponse({'code': 400, 'msg': '验证码提交失败请重新获取'})
            # 验证码不一致的返回提示信息
            if code.upper() != session_code.upper():
                return JsonResponse({'code': 400, 'msg': '验证码输入错误'})
            #根据用户名查询用户
            #返回QuerySet；加入values()  QuerySet里是字典，不加是对象
            user_list = User.objects.values().filter(username=username,isValid=1, state=1)
            #如果查询不到用户，返回错误提示
            if len(user_list) == 0:
                return JsonResponse({'code':400, 'msg':'该用户信息不存在或未审核'})

            if len(user_list) > 1:
                return JsonResponse({'code':400, 'msg':'账号异常，请联系管理员'})

            #查询到用户后，下一步密码匹配
            user = user_list[0]
            md5_password = md5((password+user['salt']).encode(encoding='utf-8')).hexdigest()

            #密码不匹配，返回错误提示
            if user['password'] != md5_password:
                return JsonResponse({'code':400, 'msg':'用户名或密码输入错误'})

            #密码匹配，登录成功，将用户登录信息存储至session
            session_user = {'id':user['id'], 'username':user['username']}
            request.session['user'] = session_user

            #接收保持登录参数
            remeber_me = request.POST.get('remember_me')
            if '1' == remeber_me:
                request.session.set_expiry(60*60*24*7) #七天后失效
            else:
                request.session.set_expiry(0)#关闭浏览器session失效

            return JsonResponse({'code':200, 'msg':'登录成功'})

        except Exception as e:
            return JsonResponse({'code':400, 'msg':'登录失败'})



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



#首页编写
@require_GET
def index(request):
    """首页"""
    return render(request, 'index.html')

#clickJacking 点击劫持
#当恶意站点诱使用户点击他们加载隐藏框架或iframe中的另一个站点的隐藏元素时，会发生这种类型的攻击。
@xframe_options_exempt #装饰器
@require_GET
def welcome(request):
    """欢迎页"""
    return render(request, 'welcome.html')


#账号审核  有问题需重新修改
@xframe_options_exempt
def audit_account(request):
    """账号审核"""
    if request.method == 'GET':
        """跳转审核账号页面"""
        return render(request, 'audit_account.html')

    if request.method == 'POST':
        try:
            #接收参数
            ids = request.POST.get('id')
            state = request.POST.get('state')
            #修改状态信息，0未审核 1审核通过 -1黑名单
            User.objects.filter(id__in=ids).update(state=state, updateDate=datetime.now())

            return JsonResponse({'code':200, 'msg':'操作成功'})
        except Exception as e:
            return JsonResponse({'code':400, 'msg':'操作失败'})

@require_GET
def select_user_list(request):
    """查询所有账号信息"""
    try:
        #获得第几页
        # page_num = request.GET.get('page')
        page_num = request.GET.get('page')
        #获取每页多少条
        page_size = request.GET.get('limit')
        #获取用户名
        username = request.GET.get('username')
        #获取审核状态
        state = request.GET.get('state')
        #查询所有账号信息，如果有条件，待条件查询
        # user_list = None
        user_list = None
        if username and state:
            user_list = User.objects.values().filter(isValid=1, username__icontains=username,
                                                     state=state).all().order_by('-id')
        elif username:
            user_list = User.objects.values().filter(isValid=1, username__icontains=username).all().order_by('-id')
        elif state:
            user_list = User.objects.values().filter(isValid=1, state=state).all().order_by('-id')

        else:
            user_list = User.objects.values().filter(isValid=1).all().order_by('-id')

        #初始化分页对象
        # p = Paginator(user_list, page_size)
        p = Paginator(user_list, page_size)
        #获取指定页数的数据
        # data = p.page(page_num).object_list
        data = p.page(page_num).object_list
        #返回总条数
        count = p.count
        #返回数据，按照layuimini要求格式构建
        context = {
            'code': 0,
            'msg': '',
            'count': count,
            'data':list(data)

        }
        # context = {'code': 0, 'msg': '', 'count': count, 'data': list(data)}
        return JsonResponse(context)



    except Exception as e:
        return JsonResponse({'code':400,'msg':'error'})

#基本资料
@xframe_options_exempt
def settings(request):
    """基本资料"""
    if request.method == 'GET':
        #从session中获取登录账号信息
        session_user = request.session.get('user')
        #获取id
        id = session_user['id']
        #根据id查询用户信息
        user = User.objects.values('id','username','password','email','phone').filter(isValid=1,id=id)

        #跳转基本资料页面
        return render(request,'settings.html',user[0])
    if request.method == 'POST':
        try:
            #获取基本资料
            id = request.POST.get('id')
            truename = request.POST.get('truename')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            #根据id查询
            user = User.objects.get(id=id)
            try:
                #如果邮箱已经存在，提示错误
                if email and email != user.email:
                    User.objects.get(email=email)
                    return JsonResponse({'code':400,'msg':'邮箱已存在，请重新添加'})
            except Exception as e:
                #如果进入异常，说明邮箱不存在可以使用
                pass
            #根据id查询，然后修改基本资料
            User.object.filter(id=id).update(truename=truename,
                                             email=email,
                                             phone=phone,
                                             updateDate=datetime.now())
            return JsonResponse({'code':200,'msg':'操作成功'})

        except Exception as e:
            return JsonResponse({'code':400,'msg':'操作失败'})

#退出登录/安全退出
def logout(request):
    #清楚session
    request.session.flush()
    #重定向登录
    return redirect('system:login')

#修改密码
@xframe_options_exempt
def password(request):
    """修改密码"""
    if request.method == 'GET':
        #跳转修改密码页面
        return render(request,'password.html')

    if request.method == 'POST':
        try:
            # 获取新旧密码
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            # 从 session 中获取登录账号信息
            session_user = request.session.get('user')
            # 获取 id
            id = session_user['id']
            # 根据 id 查询用户信息
            user = User.objects.values().filter(isValid=1, id=id)[0]
            # 使用用户输入的旧密码 + 盐加密以后和数据库密码进行匹配
            # md5 + 盐将用户输入的旧密码加密
            md5_password = md5((old_password + user['salt']).encode(encoding='utf-8')).hexdigest()
            # 旧密码不匹配，返回错误提示
            if user['password'] != md5_password:
                return JsonResponse({'code': 400, 'msg': '旧的密码输入错误'})
            # 旧密码匹配，修改密码
            # 准备盐
            salt = generate_code()
            # md5 + 盐进行新密码加密
            md5_password = md5((new_password + salt).encode(encoding='utf-8')).hexdigest()
            # 根据 id 查询，然后修改密码
            User.objects.filter(id=id).update(password=md5_password, salt=salt,
                                              updateDate=datetime.now())
            return JsonResponse({'code': 200, 'msg': '操作成功'})

        except Exception as e:
            return JsonResponse({'code':400,'msg':'操作失败'})

#权限管理----查询菜单
@xframe_options_exempt
@require_GET
def module_index(request):
    """菜单管理首页"""
    return render(request,'module/module.html')


@require_GET
def slelct_module(request):
    """查询所有模块信息"""
    try:
        #查询
        #{‘模块属性名’：‘select DATE_FORMAT(数据库列名，’格式化样式‘)}
        select = {'createDate':"select DATE_FORMAT(create_date,'%%Y-%%m-%%d %%H:%%i:%%s')",
                  'updateDate':"select DATE_FORMAT(update_date,'%%Y-%%m-%%d %%H:%%i:%%s')"}
        #如果使用后台格式化日期，必须将要格式化的列展示在values()参数中
        queryset = Module.objects.extra(select=select).values('id','parent','module_name','module_style',
                                       'grade','opt_value','url','update_date').order_by('id').all()

        return JsonResponse(list(queryset), safe=False)
    except Exception as e:
        pass


@require_GET
def index_init(request):
    """首页菜单初始化"""
    context = {
        "homeInfo":{
            "title":"首页",
            "href":"welcome"
        },
        "logoInfo":{
            "title":"CRM-智能办公",
            "image":"static/images/logo.png",
            "href":""
        }
    }
    #初始菜单
    menuInfo = []
    #查询所有一级菜单
    first_module = Module.objects.values('id','moduleName','moduleStyle','url','orders')\
                                    .filter(grade=0).order_by('orders').all()

    # first_module = Module.objects.values('id', 'module_name', 'module_style', 'url', 'orders')\
    #               .filter(grade=0).order_by('orders').all()

    #从session获取当前用户信息
    user = request.session.get('user')
    u = User.objects.get(id=user['id'])
    #获取用户的所有角色ID
    # role_id = u.roles.values_list('id',flat=True).all()
    role_id = u.roles.values_list('id', flat=True).all()
    #根据角色ID查询模块ID
    # module_id = Permission.objects.values_list('module',flat=True).filter(role__id__in=role_id)

    module_id = Permission.objects.values_list('module', flat=True).filter(role__id__in=role_id)

    for m1 in first_module:
        if m1['id'] not in module_id:
            continue
        #初始化一级菜单
        first = {
            "title": m1['moduleName'],
            "icon": m1['moduleStyle'],
            "href": m1['url'],
            "target": "_self"
        }
        #将一级菜单添加至菜单数组
        menuInfo.append(first)
        #初始化子菜单数组
        child = []
        # 查询当前菜单的的下级菜单
        second_module = Module.objects.values('id','moduleName','moduleStyle','url')\
                                            .filter(parent=m1['id']).order_by('id').all()

        for m2 in second_module:
            if m2['id'] not in module_id:
                continue
            second = {
                "title": m2['moduleName'],
                "icon": m2['moduleStyle'],
                "href": m2['url'],
                "target": "_self"
            }
            #将二级菜单添加至菜单数组
            child.append(second)

        #将子菜单数组添加至父采单
        first['child'] = child

    context['menuInfo'] = menuInfo

    return JsonResponse(context)








