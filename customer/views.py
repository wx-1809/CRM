from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.clickjacking import xframe_options_exempt

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
