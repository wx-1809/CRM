import random
import string
from datetime import datetime
from hashlib import md5

from captcha.image import ImageCaptcha
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, redirect

from CRM.common import Message
from .models import User
from .models import Module
from .models import Permission
from .models import Role
from .models import UserRole

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
    code = generate_code()
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
# @login_required
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
            ids = request.POST.get('ids')
            state = request.POST.get('state')
            #修改状态信息，0未审核 1审核通过 -1黑名单
            User.objects.filter(pk=ids).update(state=state, updateDate=datetime.now())

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

        p = Paginator(user_list, page_size)
        #获取指定页数的数据

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
def select_module(request):
    """查询所有模块信息"""
    try:
        #查询
        #{‘模块属性名’：‘select DATE_FORMAT(数据库列名，’格式化样式‘)}
        select = {'createDate':"select DATE_FORMAT(create_date,'%%Y-%%m-%%d %%H:%%i:%%s')",
                  'updateDate':"select DATE_FORMAT(update_date,'%%Y-%%m-%%d %%H:%%i:%%s')"}
        #如果使用后台格式化日期，必须将要格式化的列展示在values()参数中
        queryset = Module.objects.extra(select=select).values('id','parent','moduleName','moduleStyle',
                                       'grade','optValue','url','createDate','updateDate').order_by('id').all()

        return JsonResponse(list(queryset), safe=False)
    except Module.DoesNotExist as e:
        pass



#权限管理----添加/修改菜单
@xframe_options_exempt
@require_GET
def module_create_or_update(request):
    """添加/修改菜单页面"""
    #获取grade和parentId
    grade = request.GET.get('grade')
    parentId = request.GET.get('parentId')
    context={
        'grade':grade,
        'parentId':parentId
    }
    #获取id如果存在的话说明是修改
    id = request.GET.get('id')
    if id:
        module = Module.objects.get(pk=id)
        context['module'] = module
        context['parentId'] = module.parent_id

    return render(request,'module/add_update.html',context)

@csrf_exempt
@require_POST
def create_module(request):
    """添加模块信息"""
    try:
        #接收参数
        data = request.POST.dict()
        data.pop('id')
        #如果权限值已存在，提示错误
        optValue = data.get('optValue')
        Module.objects.get(optValue=optValue)
        return JsonResponse({'code':400, 'msg':'权限值已存在'})
    except Module.DoesNotExist as e:
        pass

    #如果有父级菜单查询父级对象插入
    parentId = data.pop('parentId')
    if parentId and parentId == '-1':
        pass
    else:
        p = Module.objects.get(pk=parentId)
        data['parent'] = p

    #添加数据
    Module.objects.create(**data)
    return JsonResponse({'code':200,'msg':'添加成功'})


@csrf_exempt
@require_POST
def update_module(request):
    """修改模块信息"""
    try:
        #接收参数
        data = request.POST.dict()
        data.pop('parentId')
        id = data.pop('id')

        #如果权限值被修改，判断是否存在，已存在，提示错误
        optValue = data.get('optValue')
        #查询原来的模块信息
        m = Module.objects.get(pk=id)
        #判断是否权限值被修改
        if optValue != m.optValue:
            #判断是否存在
            Module.objects.get(optValue=optValue)
            return JsonResponse({'code':400,'msg':'权限值已存在'})

    except Module.DoesNotExist as e:
        pass

    #修改数据
    Module.objects.filter(pk=id).update(**data, updateDate=datetime.now())
    return JsonResponse({'code':200,'msg':'修改成功'})


#删除模块
@csrf_exempt
@require_POST
def delete_module(request):
    """删除模块信息"""
    try:
        #接收参数
        id = request.POST.get('id')
        #查询是否有子项
        Module.objects.get(parent=id)
        return JsonResponse({'code':400, 'msg':'请先删除子项'})
        # pass
    except Module.DoesNotExist as e:
        pass

    #删除模块
    Module.objects.filter(pk=id).delete()
    return JsonResponse({'code':200,'msg':'删除成功'})


#角色管理----查询角色
@xframe_options_exempt
@require_GET
def role_index(request):
    """角色管理首页"""
    return render(request,'role/role.html')

@require_GET
def select_role(requset):
    """查询所有角色信息"""
    try:
        #获取第几页
        page_num = requset.GET.get('page',1)#添加默认值，防止没有参数导致异常错误
        #获取每页多少条
        page_size = requset.GET.get('limit',10)#添加默认值，防止没有参数导致异常错误
        #查询
        #{‘模型属性名’：‘select DATE_FORMAT(数据库列明，‘格式化样式’)’}
        select = {'createDate':"select DATE_FORMAT(create_date,'%%Y-%%m-%%d %%H:%%i:%%s')",
                  'updateDate':"select DATE_FORMAT(update_date,'%%Y-%%m-%%d %%H:%%i:%%s')"}
        #如果使用后台格式化日期，必须将要格式化列展示在valus()参数中
        queryset = Role.objects.extra(select=select).values('id','roleName','roleRemark',
                                    'createDate','updateDate').order_by('id').all()
        #待条件查询
        roleName = requset.GET.get('roleName')
        if roleName:
            queryset = queryset.filter(roleName__icontains=roleName)
        #初始化分页对象
        p = Paginator(queryset,page_size)
        #获取指定页数的数据
        data = p.page(page_num).object_list
        #返回总条数
        count = p.count
        #返回数据，按照layuimini要求格式构建
        context = {
            'code':0,
            'msg':'',
            'count':count,
            'data':list(data)
        }

        return JsonResponse(context)
        # pass
    except Module.DoesNotExist as e:
        pass

#添加/修改角色
@xframe_options_exempt
@require_GET
def role_create_or_update(request):
    """添加/修改角色页面"""
    #获取角色主键
    id = request.GET.get('id')
    context = None
    if id:
        context = {'role': Role.objects.get(pk=id)}
    return render(request, 'role/add_update.html', context)

@csrf_exempt
@require_POST
def create_role(request):
    """添加角色信息"""
    try:
        #接收参数
        data = request.POST.dict()
        data.pop('id')
        #如果角色已存在提示错误
        roleName = data.get('roleName')
        Role.objects.get(roleName=roleName)
        return JsonResponse({'code':400,'msg':'角色已存在'})
        # pass
    except Role.DoesNotExist as e:
        pass

    #添加数据
    Role.objects.create(**data)
    return JsonResponse({'code':200, 'msg':'添加成功'})

@csrf_exempt
@require_POST
def update_role(request):
    """更新角色信息"""
    try:
        #接收参数
        data = request.POST.dict()
        id = data.pop('id')
        #如果角色被修改，判断是否存在，已存在，提示错误
        roleName = data.get('roleName')
        #查询原来的角色信息
        r = Role.objects.get(pk=id)
        #判断角色是否被修改
        if roleName != r.roleName:
            #判断是否存在
            Role.objects.get(roleName=roleName)
            return JsonResponse({'code':400,'msg':'角色名已存在'})
    except Role.DoesNotExist as e:
        pass

    #修改数据
    data['updateDate'] = datetime.now()
    Role.objects.filter(pk=id).update(**data)
    return JsonResponse({'code':200,'msg':'修改成功'})

@csrf_exempt
@require_POST
def delete_role(request):
    """删除角色信息"""
    # 接收参数
    data = request.POST.dict()
    id = data.pop('id')

    Role.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())
    UserRole.objects.filter(user__id__in=id).update(isValid=0, updateDate=datetime.now())
    
    return JsonResponse({'code':200,'msg':'删除成功'})



#角色授权---角色内容
@xframe_options_exempt
@require_GET
def role_grant(request):
    """跳转角色授权页面"""
    #获取角色主键
    id = request.GET.get('id')
    context = {'id':id}
    return render(request,'role/grant.html',context)

@require_GET
def select_role_module(request):
    """查询所有权限及当前角色所拥有的权限"""
    #获得角色主键
    roleId = request.GET.get('id')
    #查询所有权限(模块)
    module = list(Module.objects.values('id','parent','moduleName').all())
    #查询角色已拥有的权限(资源)
    roleModule = Permission.objects.values_list('module',flat=True).filter(role__id=roleId).all()
    #设置checked
    for m in module:
        if m.get('id') in roleModule: #数据库的字段名
            m['checked'] = 'true'
        else:
            m['checked'] = 'false'

    #返回数据
    return JsonResponse(module, safe=False)

@csrf_exempt
@require_POST
def role_relate_module(request):
    """角色关联模块"""
    try:
        #接收参数
        module_checked_id = request.POST.get('module_checked_id')
        role_id = request.POST.get('role_id')
        #删除该角色拥有的所有权限
        Permission.objects.filter(role__id=role_id).delete()
        #如果模块为空，则直接return
        if not module_checked_id:
            return JsonResponse({'code':200,'msg':'操作成功'})

        #查询角色和模块
        role = Role.objects.get(pk=role_id)
        module = Module.objects.filter(pk__in=module_checked_id.split(',')).all() #以‘,’分隔获得相应的内容；
        #循环插入数据
        for m in module:
            Permission.objects.create(role=role, module=m)
        # return JsonResponse({'code':200,'msg':'操作成功'})
        return JsonResponse(Message(msg='操作成功').result())
    except Exception as e:
        # return JsonResponse({'code':400, 'msg':'操作失败'})
        return JsonResponse(Message(code=400, msg='操作失败').result())


#用户管理
#查询用户
@xframe_options_exempt
@require_GET
def user_index(request):
    """用户管理首页"""
    return render(request, 'user/user.html')

@require_GET
def select_user(request):
    """查询用户的所有信息"""
    try:
        #获取第几页
        page_num = request.GET.get('page',1)
        #获取每页多少条
        page_size = request.GET.get('limit', 10)
        #查询
        #{‘模型属性名’：‘select DATE_FORMAT(数据库列名，‘’格式化样式)’}
        select = {'create_date':"select DATE_FORMAT(create_date,'%%Y-%%m-%%d %%H:%%i:%%s')",
                  'update_date':"select DATE_FORMAT(update_date,'%%Y-%%m-%%d %%H:%%i:%%s')"}
        #如果后台使用格式化日期，必须将要格式化的列展示在values()参数中
        queryset = User.objects.extra(select=select).values('id','username','truename','email','phone',
                                                            'create_date','update_date').order_by('-id').all()
        #接收参数，按条件查询
        username = request.GET.get('username')
        if username:
            queryset = queryset.filter(username__icontains=username)
        email = request.GET.get('email')
        if email:
            queryset = queryset.filter(email__icontains=email)
        phone = request.GET.get('phone')
        if phone:
            queryset = queryset.filter(phone__icontains=phone)
        #初始化分页对象
        p = Paginator(queryset, page_size)
        #获取指定页数的数据
        data = p.page(page_num).object_list
        #返回总条数
        count = p.count
        #返回数据，按照layuimini要求格式构建
        context = {
            'code': 0,
            'msg':'',
            'count':count,
            'data':list(data)
        }

        return JsonResponse(context)
        # pass
    except User.DoesNotExist as e:
        pass

#添加用户
@xframe_options_exempt
@require_GET
def user_create_or_update(request):
    """跳转添加或修改用户界面"""
    #获取用户主键
    id = request.GET.get('id')
    context = None
    if id:
        context = {'user': User.objects.get(id=id)}

    return render(request,'user/add_update.html',context)

@require_GET
def select_role_for_user(request):
    """用户管理查询角色"""
    try:
        #查询所有角色
        role = Role.objects.values('id','roleName').all().order_by('id')
        #返回数据
        context = {'role': list(role)}
        #获取用户主键
        id  = request.GET.get('id')
        if id:
            #查询用户所有角色
            roleIds = UserRole.objects.values_list('role',flat=True).filter(user__id=id).all() #isequall=role_id
            userRole = Role.objects.values('id','roleName').filter(pk__in=roleIds).all()
            context['userRole'] = list(userRole)

        return JsonResponse(context, safe=False)
    except Role.DoesNotExist as e:
        pass


@csrf_exempt
@require_POST
def create_user(request):
    """添加用户信息"""
    try:
        #接收参数
        data = request.POST.dict()
        # print(data)
        data.pop('id')
        #如果用户名已存在，提示错误
        username = data.get('username')
        User.objects.get(username=username)

        return  JsonResponse({'code':400,'msg':'该用户已存在'})
    except User.DoesNotExist as e:
        pass

    try:
        #如果邮箱已存在，提示错误
        email = data.get('email')
        User.objects.get(email=email)

        return JsonResponse({'code':400, 'msg':'邮箱已存在，请重新添加'})
    except User.DoesNotExist as e:
        pass


    #加密密码
    #使用md5加密
    data['password'] = md5('123456'.encode(encoding='utf-8')).hexdigest()
    role_ids = data.pop('select') #有bug
    #添加数据
    user = User.objects.create(**data)

    """
    #插入用户角色中间表
    if len(role_ids) > 0:
        roles = Role.objects.filter(pk__in=role_ids.split(',')).all()
        for role in roles:
            UserRole.objects.create(user=user, role=role)
    """
    #插入用户角色中间表
    result = create_userrole(role_ids, user, is_create=True)

    return JsonResponse(result)
    # return JsonResponse({'code': 200, 'msg': '创建成功'})

def create_userrole(role_ids,user,is_create=False):
    """添加用户角色中间表"""
    if not is_create:
        #删除所有该用户的角色
        #user.userrole_set.all().delete()
        UserRole.objects.filter(user__id=user.id).delete()
    if len(role_ids) > 0:
        roles = Role.objects.filter(pk__in=role_ids.split(',')).all()
        for role in roles:
            UserRole.objects.create(user=user, role=role)

    return {'code':200,'msg':'操作成功'}


#修改用户
@csrf_exempt
@require_POST
def update_user(request):
    """修改用户信息"""
    try:
        #接收参数
        data = request.POST.dict()

        id = data.pop('id')
        user = User.objects.get(id=id)
        username = data.get('username')
        #如果用户名被更改，判断用户名是否存在
        if username and username != user.username:
            User.objects.get(username=username)
            return JsonResponse({'code':200,'msg':'用户名已存在，请重新添加'})

    except User.DoesNotExist as e:
        pass


    try:
        #如果邮箱被更改，判断邮箱是否存在
        email = data.get('email')
        if email and email != user.email:
            User.objects.get(email=email)
            return  JsonResponse({'code':200,'msg':'邮箱已存在，请重新添加'})
    except User.DoesNotExist as e:
        pass


    role_ids = data.pop('select')
    """
    # 删除所有该用户的角色 
    UserRole.objects.filter(user__id=id).delete() 
    if len(role_ids) > 0: 
        # 修改用户角色中间表 
        roles = Role.objects.filter(pk__in=role_ids.split(',')).all() 
        for role in roles: 
            UserRole.objects.create(user=user, role=role)
    """
    #修改数据
    data['updateDate'] = datetime.now()
    User.objects.filter(id=id).update(**data)
    #修改用户角色中间表
    result = create_userrole(role_ids,user)
    return JsonResponse(result)


#删除用户
@csrf_exempt
@require_POST
def delete_user(request):
    """删除用户信息"""
    #接收参数
    ids = request.POST.getlist('ids')
    #逻辑删除
    User.objects.filter(pk__in=ids).update(isValid=0, updateDate=datetime.now())
    #删除用户所有角色
    UserRole.objects.filter(user__id__in=ids).delete()

    return JsonResponse({'code':200,'msg':'删除成功'})



#修改登录index界面，即将index界面初始化
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


@require_GET
def select_customer_manager(request):
    """查询客户经理（指派人）"""
    user_list = User.objects.values("id",'username','truename').filter(isValid=1).order_by('-id').all()

    return JsonResponse(list(user_list), safe=False)










