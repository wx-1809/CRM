from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from customer.models import Customer, OrdersDetail, CustomerOrders, CustomerLoss, CustomerReprieve


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


#订单查看
@xframe_options_exempt
@require_GET
def order_index(request):
    """跳转订单查看页面"""
    #接收参数
    id = request.GET.get('id')
    #查询客户信息
    c = Customer.objects.get(pk=id)
    context = {
        'id':id,
        'khno': c.khno,
        'name': c.name,
        'fr': c.fr,
        'address': c.address,
        'phone': c.phone
    }

    return render(request,'customer/customer_order.html',context)


@xframe_options_exempt
@require_GET
def select_orderlist_by_customerid(request):
    """根据客户主键查询订单"""
    try:
        #获取第几页
        page_num = request.GET.get('page')
        #获取每页多少条
        page_size = request.GET.get('limit')
        #获取客户主键
        id = request.GET.get('id')
        #查询订单列表
        order_list = CustomerOrders.objects.values().filter(customer=id)
        # order_list = CustomerOrders.objects.values().filter(customer=id)
        #初始化分页对象
        p = Paginator(order_list, page_size)
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

    except Exception as e:
        return JsonResponse({'code':400,'msg':'error'})

#订单详情
@xframe_options_exempt
@require_GET
def order_detail_index(request):
    """跳转订单详情页面"""
    #接收参数
    id = request.GET.get('id')
    #查询订单信息
    o = CustomerOrders.objects.get(pk=id)
    context = {
        'id':id,
        'orderNo':o.orderNo,
        'totalPrice':o.totalPrice,
        'address':o.address,
        'state':o.get_state_display
    }

    return render(request,'customer/customer_order_detail.html',context)

@require_GET
def select_orderdetaild_by_orderid(request):
    """根据订单主题查询订单详情"""
    try:
        #获得第几页
        page_num = request.GET.get('page')
        #获得每页多少条
        page_size = request.GET.get('limit')
        #获得订单主键
        id = request.GET.get('id')
        #查询订单详情
        orderdetail_list = OrdersDetail.objects.values().filter(order=id)
        #初始化分页对象
        p = Paginator(orderdetail_list, page_size)
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
    except Exception as e:
        return JsonResponse({'code':400, 'msg':'error'})


# #定时任务添加
# def my_task():
#     print("Hello Scheduler")
#
# scheduler = BackgroundScheduler() # 创建一个调度器对象
# scheduler.add_job(my_task, 'interval', seconds=2)#创建一个任务
# scheduler.start()#启动任务

#添加流失客户
def create_customer_loss():
    """添加暂缓流失客户"""
    try:
        #创建游标对象
        cursor = connection.cursor()
        #编写SQL
        sql= """
            SELECT 
                c.id id, 
                c.khno cusNo, 
                c.NAME cusName, 
                c.cus_manager cusManager, 
                max( co.order_date ) lastOrderTime 
            FROM
                t_customer c 
                LEFT JOIN t_customer_order co ON c.id = co.cus_id 
            WHERE
                c.is_valid = 1 
                AND c.state = 0 
                AND NOW() > DATE_ADD( c.create_date, INTERVAL 6 MONTH ) 
                AND NOT EXISTS ( 
                SELECT DISTINCT 
                    o.cus_id 
                FROM
                    t_customer_order o
                WHERE
                    o.is_valid = 1 
                    AND NOW() < DATE_ADD( o.order_date, INTERVAL 6 MONTH )
                    AND c.id = o.cus_id 
                )
        GROUP BY
            c.id;
        """
        #执行SQL
        cursor.execute(sql)
        #返回多条结果行
        customer_loss_tuple = cursor.fetchall()#查询当前sql执行后所有的记录，返回元组
        #关闭游标
        cursor.close()
        #将元组转换为列表
        customer_loss_id = []#暂缓流失客户id列表
        customer_loss_list = []#暂缓流失客户列表
        for cl in customer_loss_tuple:
            customer_loss_id.append(cl[0])
            customer_loss_list.append(CustomerLoss(cusNo=cl[1],
                                                   cusName=cl[2],
                                                   cusManager=cl[3],
                                                   lastOrderTime=cl[4],
                                                   state=0))  # 暂缓流失
        #批量插入客户流失表
        CustomerLoss.objects.bulk_create(customer_loss_list)
        Customer.objects.filter(id__in=customer_loss_id).update(state=1, updateDate=datetime.now())
    except Exception as e:
        print(e)
    finally:
        #关闭链接
        connection.close()

# 创建一个调度器对象
scheduler = BackgroundScheduler()
# # 创建一个任务
scheduler.add_job(create_customer_loss, 'interval', minutes=1)
# # 启动任务
scheduler.start()
# 结束任务
# scheduler.end()

#客户流失管理列表
@xframe_options_exempt
@require_GET
def loss_index(request):
    """跳转客户流失管理首页"""
    return render(request, 'customer/customer_loss.html')

@require_GET
def select_loss_list(request):
    """查询所有客户流失信息"""
    try:
        #获取第几页
        page_num = request.GET.get('page')
        #获取每页多少条
        page_size = request.GET.get('limit')
        #获取客户编号
        cusNo = request.GET.get('cusNo')
        #获取客户名称
        cusName = request.GET.get('cusName')
        # 获取客户状态
        state = request.GET.get('state')
        #查询所有
        loss_list = CustomerLoss.objects.values().all().order_by('-lastOrderTime')
        #如果有条件参数，带条件查询
        if cusNo:
            loss_list = loss_list.filter(cusNo__icontains=cusNo)
        if cusName:
            loss_list = loss_list.filter(cusName__icontains=cusName)
        if state:
            loss_list = loss_list.filter(state=state)

        #初始化分页对象
        p = Paginator(loss_list, page_size)
        #获取指定页数数据
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
    except Exception as e:
        return JsonResponse({'code':400, 'msg':'error'})


#添加暂缓/查看详情
@xframe_options_exempt
@require_GET
def loss_detail_index(request):
    """根据客户流失主键查询"""
    try:
        # 获取客户流失主键
        id = request.GET.get('id')
        # 查询客户流失信息
        cl = CustomerLoss.objects.get(pk=id)
        context = {'cl': cl}

        return render(request, 'customer/customer_reprieve.html',context)

    except CustomerLoss.DoesNotExist as e:
        pass

@require_GET
def select_reprieve_by_lossid(request):
    """根据客户流失主键查询流失措施"""
    try:
        #获取第几页
        page_num = request.GET.get('page')
        #获取每页第几条
        page_size = request.GET.get('limit')
        #获取客户流失主键
        id = request.GET.get('id')
        #查询
        # cp_list = CustomerReprieve.objects.values().filter(customerLoss=id).order_by('-id')
        cp_list = CustomerReprieve.objects.values().filter(customerLoss=id).order_by('-id')
        #初始化分页对象
        p = Paginator(cp_list, page_size)
        #获取指定页数的数据
        data = p.page(page_num).object_list
        #总条数
        count = p.count
        #返回数据，按照layuimini要求格式构建
        context = {
            'code': 0,
            'msg':'',
            'count':count,
            'data':list(data)
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code':400, 'msg':'error'})


#添加/修改/删除暂缓
@xframe_options_exempt
@require_GET
def reprieve_index(request):
    """添加客户暂缓页面"""
    #获取客户流失主键
    lossId = request.GET.get('lossId')
    context = {
        'lossId': lossId
    }
    #获取客户暂缓主键
    id = request.GET.get('id')
    if id:
        cp = CustomerReprieve.objects.get(pk=id)
        context['id'] = id
        context['cp'] = cp

    return render(request, 'customer/customer_reprieve_add_update.html', context)

@csrf_exempt
@require_POST
def create_reprieve(request):
    """添加客户暂缓"""
    #获取客户流失主键
    lossId = request.POST.get('lossId')
    #获取客户暂缓措施
    measure = request.POST.get('measure')
    #查询流失客户数据
    cl = CustomerLoss.objects.get(pk=lossId)
    data = {
        'customerLoss': cl,
        'measure': measure
    }
    #添加
    CustomerReprieve.objects.create(**data)

    return JsonResponse({'code':200, 'msg':'添加成功'})

@csrf_exempt
@require_POST
def update_reprieve(request):
    """修改客户暂缓"""
    #获取客户暂缓主键
    id = request.POST.get('id')
    #获取客户暂缓措施
    measure = request.POST.get('measure')
    data = {
        'measure': measure,
        'updateDate': datetime.now()
    }
    # 添加
    CustomerReprieve.objects.filter(pk=id).update(**data)

    return JsonResponse({'code': 200, 'msg': '修改成功'})

@csrf_exempt
@require_POST
def delete_reprieve(request):
    """删除客户暂缓"""
    #获取客户暂缓主键
    id = request.POST.get('id')
    #逻辑删除
    CustomerReprieve.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())

    return JsonResponse({'code':200, 'msg':'删除成功'})


#确认流失
@csrf_exempt
@require_POST
def update_lossreason_by_lossid(request):
    """确认流失"""
    #获取流失客户主键
    lossId = request.POST.get('lossId')
    #获取流失原因
    lossReason = request.POST.get('lossReason')
    #根据客户流失主键查询
    cl = CustomerLoss.objects.get(pk=lossId)
    #重新赋值
    cl.lossReason = lossReason
    cl.state = 1
    cl.confirmLossTime = datetime.now()
    #保存
    cl.save()
    #修改客户表状态
    Customer.objects.filter(khno=cl.cusNo).update(state=2, updateDate=datetime.now())

    return JsonResponse({'code':200, 'msg':'保存成功'})
















































