from datetime import datetime

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from customer.models import Customer


@xframe_options_exempt
def customer_index(request):
    """跳转客户信息管理首页"""
    return render(request, 'customer/customer.html')

#客户信息列表展示
def select_customer_list(request):
    """查询所有客户信息"""
    try:
        # 获取第几页
        page_num = request.GET.get('page')
        # 获取每页多少条
        page_size = request.GET.get('limit')
        # 获取客户名称
        name = request.GET.get('name')
        # 获取客户编号
        khno = request.GET.get('khno')
        # 获取客户等级
        level = request.GET.get('level')
        # 查询所有客户信息，如果有条件，带条件查询
        customer_list = None
        if name and khno and level:
            customer_list = Customer.objects.values().filter(name__icontains=name, khno__icontains=khno,
                                                             level=level).all().order_by('-id')
        elif name and khno:
            customer_list = Customer.objects.values().filter(name__icontains=name, khno__icontains=khno)\
                                                    .all().order_by('-id')
        elif name and level:
            customer_list = Customer.objects.values().filter(name__icontains=name, level=level).all().order_by('-id')
        elif khno and level:
            customer_list = Customer.objects.values().filter(khno__icontains=khno, level=level).all().order_by('-id')
        elif name:
            customer_list = Customer.objects.values().filter(name__icontains=name).all().order_by('-id')
        elif khno:
            customer_list = Customer.objects.values().filter(khno__icontains=khno).all().order_by('-id')
        elif level:
            customer_list = Customer.objects.values().filter(level=level).all().order_by('-id')
        else:
            customer_list = Customer.objects.values().all().order_by('-id')

        # 初始化分页对象
        p = Paginator(customer_list, page_size)
        # 获取指定页数的数据
        data = p.page(page_num).object_list
        # 返回总条数
        count = p.count
        # 返回数据，按照 layuimini 要求格式构建
        context = {
            'code': 0,
            'msg': '',
            'count': count,
            'data': list(data)
        }
        return JsonResponse(context)

    except Exception as e:
        return JsonResponse({'code':400,'msg':'error'})


#新增或修改客户信息
@csrf_exempt
@xframe_options_exempt
def create_or_update_customer(request):
    """添加或修改客户信息"""
    if request.method == 'GET':
        # 客户主键
        id = request.GET.get('id')
        #如果客户主键存在，说明是打开修改客户信息页面
        if id:
            customer = Customer.objects.values().filter(id=id)
            return render(request, 'customer/customer_add_update.html', customer[0])
        else:
            return render(request, 'customer/customer_add_update.html')

    if request.method == 'POST':
        try:
            #接收参数
            name = request.POST.get('name')
            area = request.POST.get('area')
            cusManager = request.POST.get('cusManager')
            level = request.POST.get('level')
            xyd = request.POST.get('xyd')
            postCode = request.POST.get('postCode')
            phone = request.POST.get('phone')
            fax = request.POST.get('fax')
            website = request.POST.get('website')
            address = request.POST.get('address')
            fr = request.POST.get('fr')
            zczj = request.POST.get('zczj')
            nyye = request.POST.get('nyye')
            khyh = request.POST.get('khyh')
            khzh = request.POST.get('khzh')
            dsdjh = request.POST.get('dsdjh')
            gsdjh = request.POST.get('gsdjh')

            #添加或者修改数据
            #如果存在主键，说明修改客户信息，不生成客户编号
            id = request.POST.get('id')
            c = None
            if not id:
                #KH+时间
                khno = 'KH' + datetime.now().strftime('%Y%m%d%H%M%S')
                #添加数据
                Customer.objects.create(khno=khno, name=name, area=area, cusManager=cusManager, level=level, xyd=xyd,
                                        postCode=postCode, phone=phone, fax=fax, website=website, address=address,
                                        fr=fr, zczj=zczj, nyye=nyye, khyh=khyh, khzh=khzh, dsdjh=dsdjh, gsdjh=gsdjh)
            else:
                Customer.objects.filter(id=id).update(name=name, area=area, cusManager=cusManager, level=level,
                                                xyd=xyd, postCode=postCode, phone=phone, fax=fax, website=website,
                                                address=address, fr=fr, zczj=zczj, nyye=nyye, khyh=khyh, khzh=khzh,
                                                      dsdjh=dsdjh, gsdjh=gsdjh, updateDate=datetime.now())
            #返回提示信息
            return JsonResponse({'code':200,'msg':'保存成功'})

        except Exception as es:
            return JsonResponse({'code':400, 'msg':'保存失败'})



#删除客户信息
@csrf_exempt
@require_POST
def delete_customer(request):
    """根据主键删除客户信息"""
    try:
        id = request.POST.get('id')
        #逻辑删除
        Customer.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())
        return JsonResponse({'code':200, 'msg':'删除成功'})
        # pass
    except Exception as e:
        return JsonResponse({'code':400, 'msg':'删除失败'})























