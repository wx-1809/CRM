from datetime import datetime

import pymysql.cursors
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from CRM.common import permission_required
from dbutil import pymysql_pool
from django.db import connection



#准备数据
config = {
    'host': 'localhost',
    'port': 3306,#数据库端口
    'user': 'root',#数据库用户名
    'password':'111111',#数据库密码
    'database':'db_crm', #具体的一个库，等价于database
    'charset':'utf8',#字符集
    #默认获取的数据是元组类型，如果想要字典类型的数据
    'cursorclass': pymysql.cursors.DictCursor
}
#
# #初始化连接池对象
connect_pool = pymysql_pool.ConnectionPool(size=10, name='mysql_pool', **config)

#从连接池中获取连接
def connect():
    #从连接池中获取连接
    connection = connect_pool.get_connection()
    return connection

from customer.models import Customer, LinkMan
from sales.models import SaleChance, CusDevPlan


# @permission_required('1010')
@xframe_options_exempt
@require_GET
def sales_index(request):
    """跳转营销管理首页"""
    #营销机会管理权限值是1010
    #第一种
    #从session中获取权限值进行比较
    # user_permissions = request.session.get('user_permission')
    # if not user_permissions or '1010' not in user_permissions:
    #     return render(request, '404.html', {'msg' : '对不起，您无权限访问'})
    return render(request, 'sales/sale_chance.html')


@require_GET
def select_sale_chance_list(request):
    """分页查询营销机会"""
    try:
        #第几页
        page = request.GET.get('page', 1)
        #每页多少条
        page_size = request.GET.get('limit')
        #获取链接
        connection = connect()
        #创建游标对象
        cursor = connection.cursor()
        #编写SQL
        sql = """
            SELECT
                sc.id id, 
                sc.chance_source chanceSource,
                sc.customer_id customerId, 
                sc.customer_name customerName, 
                sc.cgjl cgjl, 
                sc.overview overview, 
                sc.link_man linkMan, 
                sc.link_phone linkPhone, 
                sc.description description, 
                sc.create_man createMan, 
                u.username assignMan, 
                sc.assign_time assignTime, 
                sc.state state, 
                sc.dev_result devResult, 
                sc.is_valid isValid,
                sc.create_date createDate, 
                sc.update_date updateDate
            FROM
                t_sale_chance sc 
            INNER JOIN t_customer c ON sc.customer_id = c.id LEFT JOIN t_user u ON sc.assign_man = u.id 
            WHERE
                sc.is_valid = 1 AND c.is_valid = 1
        """
        #如果有查询条件要重新拼写SQL
        #客户名称
        # customerName = request.GET.get('customerName')
        customerName = request.GET.get('customerName')
        #创建人
        # createMan = request.GET.get('createMan')
        createMan = request.GET.get('createMan')
        #分配状态
        # state = request.GET.get('state')
        state = request.GET.get('state')
        #开发状态(客户开发计划使用)
        # devResult = request.GET.get('devResult')
        devResult = request.GET.get('devResult')
        if customerName:
            sql += ' AND sc.customer_name like "%{}%" '.format(customerName)
            # sql += ' AND sc.customer_name like "%{}%" '.format(customerName)
        if createMan:
            # sql += ' AND sc.create_man like "%{}%" '.format(createMan)
            sql += ' AND sc.create_man like "%{}%" '.format(createMan)
        if state:
            # sql += ' AND sc.state = "{}" '.format(state)
            sql += ' AND sc.state = "{}" '.format(state)
        if devResult:
            # sql += ' AND sc.dev_result = "{}" '.format(devResult)
            sql += ' AND sc.dev_result = "{}" '.format(devResult)
        # sql += ' ORDER BY sc.id DESC;'
        sql += ' ORDER BY sc.id;'
        #执行SQL
        cursor.execute(sql)
        #返回结果
        sale_chance_list = cursor.fetchall()
        #关闭游标
        cursor.close()
        #初始化分页对象
        p = Paginator(sale_chance_list, page_size)
        #获取指定页数的数据
        data = p.page(page).object_list
        #获取总记录
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
    finally:
        #关闭连接
        connection.close()


@xframe_options_exempt
@require_GET
def create_or_update_sales(request):
    """跳转添加/修改营销机会页面"""
    #获取营销机会主键
    saleChanceId = request.GET.get('saleChanceId')
    context = None
    if saleChanceId:
        #根据营销机会主键查询
        sc = SaleChance.objects.get(pk=saleChanceId)
        context={'sc': sc}
    return render(request, 'sales/add_update.html',context)

@require_GET
def select_customer(request):
    """查询客户"""
    customer = Customer.objects.values("id", 'name').filter(isValid=1).order_by('-id').all()
    return JsonResponse(list(customer), safe=False)

@csrf_exempt
@require_POST
def create_sale_chance(request):
    """添加营销机会和联系人"""
    try:
        #接收参数
        customerId = request.POST.get('customer')
        customerName = request.POST.get('customerName')
        chanceSource = request.POST.get('chanceSource')
        linkMan = request.POST.get('linkMan')
        linkPhone = request.POST.get('linkPhone')
        cgjl = request.POST.get('cgjl')
        overview = request.POST.get('overview')
        description = request.POST.get('description')
        assignMan = request.POST.get('assignMan')
        #如果有联系人还要添加联系人表数据
        if linkMan:
            lm = LinkMan(cusId=customerId, linkName=linkMan, phone=linkPhone)
            lm.save()

        #如果有分配人，添加分配时间，分配状态为已分配
        if assignMan != '0':
            sc = SaleChance(customerId=customerId, customerName=customerName,
                            chanceSource=chanceSource, linkMan=linkMan, linkPhone=linkPhone,
                            cgjl=cgjl, overview=overview, description=description,
                            assignMan=assignMan, assignTime=datetime.now(), state=1,
                            devResult=0, createMan=request.session.get('user')['username'])
        else:
            sc = SaleChance(customerId=customerId, customerName=customerName, chanceSource=chanceSource,
                            linkMan=linkMan, linkPhone=linkPhone, cgjl=cgjl, overview=overview, description=description,
                            state=0, devResult=0, createMan=request.session.get('user')['username'])

        #插入数据
        sc.save()

        #返回提示信息
        return JsonResponse({'code':200, 'msg':'Add Success!'})

    except Exception as e:
        return JsonResponse({'code':400, 'msg':'Add Fail！'})

@csrf_exempt
@require_POST
def update_sale_chance(request):
    """修改营销机会和联系人"""
    try:
        #接收参数
        id = request.POST.get('id')
        customerId = request.POST.get('customer')
        customerName = request.POST.get('customerName')
        chanceSource = request.POST.get('chanceSource')
        linkMan = request.POST.get('linkMan')
        linkPhone = request.POST.get('linkPhone')
        cgjl = request.POST.get('cgjl')
        overview = request.POST.get('overview')
        description = request.POST.get('description')
        assignMan = request.POST.get('assignMan')
        #根据主键查询营销机会
        sc = SaleChance.objects.get(pk=id)

        #如果有联系人还要修改联系人表数据
        if linkMan != sc.linkMan:
            LinkMan.objects.filter(cusId=customerId).update(linkName=linkMan, phone=linkPhone, updateDate=datetime.now())

        #如果用户取消了分配人，要改变分配状态为未分配状态
        if assignMan == '0':
            sc.state = 0
            sc.assignMan = None
            sc.assignTime = None
        else:
            sc.state = 1
            sc.assignMan = assignMan
            sc.assignTime =datetime.now()

        #重新赋值
        sc.customerId = customerId
        sc.customerName = customerName
        sc.chanceSource = chanceSource
        sc.linkMan = linkMan
        sc.linkPhone = linkPhone
        sc.cgjl = cgjl
        sc.overview = overview
        sc.description = description
        sc.updateDate = datetime.now()

        #保存
        sc.save()

        #返回提示信息
        return JsonResponse({'code':200, 'msg':'Update Success!'})
    except Exception as e:
        return JsonResponse({'code':400, 'msg':'Updata Fail!'})


@csrf_exempt
@require_POST
def delete_sale_chance(request):
    """删除营销机会"""
    try:
        #接收参数
        ids = request.POST.get('ids')
        #获取连接
        connection = connect()
        #创建游标对象
        cursor = connection.cursor()
        #编写SQL
        sql = 'DELETE FROM t_sale_chance WHERE id IN (%s);' %ids
        #执行SQL
        result = cursor.execute(sql)
        #提交，不然无法保存增删改操作的数据和结果
        connection.commit()

        return JsonResponse({'code':200, 'msg':'Delete Success!'})
    except Exception as e:
        return JsonResponse({'code':400,'msg':'Delete Failed!'})


#客户开发计划列表
@xframe_options_exempt
@require_GET
def cus_dev_plan_index(request):
    """跳转客户开发计划管理首页"""
    return render(request, 'sales/cus_dev_plan.html')


@xframe_options_exempt
@require_GET
def cus_dev_plan_index_detail(request):
    """跳转客户开发计划详情页"""
    #接收参数
    saleChanceId = request.GET.get('saleChanceId')
    # saleChanceId = request.GET.get('id')
    # 根据主键查询营销机会
    sc = SaleChance.objects.get(pk=saleChanceId)
    print(sc)
    context = {'sc': sc}

    return render(request, 'sales/cus_dev_plan_detail.html', context)

@require_GET
def select_cus_dev_plan_list(request):
    """查询客户开发计划详细列表"""
    try:
        # 获取第几页
        page_num = request.GET.get('page', 1)
        # 获取每页多少条
        page_size = request.GET.get('limit',10)
        # 获取客户营销机会主键
        saleChanceId = request.GET.get('saleChanceId')
        #查询
        cdp_list = CusDevPlan.objects.extra(select={'planDate': 'date_format(plan_date, "%%Y-%%m-%%d")'}).\
                                            values('id', 'planItem', 'planDate', 'exeAffect', 'saleChance').\
                                            filter(saleChance=saleChanceId).order_by('id')
        # queryset = CustomerServe.objects.extra(select=select_dict).values().order_by('-id').all()
        #初始化分页对象
        p = Paginator(cdp_list, page_size)
        #获取指定页数的数据
        data = p.page(page_num).object_list
        #返回总条数
        count = p.count
        #返回数据，按照layuimini要求格式构建
        context = {
            'code':0,
            'msg': '',
            'count': count,
            'data': list(data)
        }

        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({'code':400, 'msg':'error'})



#添加/修改/删除开发计划
@xframe_options_exempt
@require_GET
def create_or_update_cus_dev_plan(request):
    """跳转客户开发计划添加/修改页面"""
    #获取营销机会主键
    saleChanceId = request.GET.get('saleChanceId')

    #获取客户开发计划主键
    id = request.GET.get('id')
    context = {'saleChanceId': saleChanceId}

    if id:
        cusDevPlan = CusDevPlan.objects.get(pk=id)
        context['cusDevPlan'] = cusDevPlan

    return render(request, 'sales/cus_dev_plan_add_update.html', context)


@csrf_exempt
@require_POST
def create_cus_dev_plan(request):
    """添加客户开发计划"""
    #接收参数
    data = request.POST.dict()

    #弹出营销机会主键
    saleChanceId = data.pop('saleChanceId')

    #删除主键
    del data['id']

    #获取营销机会对象
    sc = SaleChance.objects.get(pk=saleChanceId)
    data['saleChance'] = sc
    # data['']

    # 添加客户开发计划
    CusDevPlan.objects.create(**data)
    # 修改营销机会的开发状态为开发中
    sc.devResult = 1
    sc.updateDate = datetime.now()
    sc.save()
    # print("内容" % data)

    return JsonResponse({'code': 200, 'msg': '添加成功'})


@csrf_exempt
@require_POST
def update_cus_dev_plan(request):
    """修改客户开发计划"""
    # 接收参数
    data = request.POST.dict()
    # 弹出营销机会主键
    saleChanceId = data.pop('saleChanceId')
    # 删除主键
    id = data.pop('id')

    # 修改时间
    data['updateDate'] = datetime.now()

    # 修改客户开发计划
    CusDevPlan.objects.filter(pk=id).update(**data)

    return JsonResponse({'code': 200, 'msg': '修改成功'})


@csrf_exempt
@require_POST
def delete_cus_dev_plan(request):
    """删除客户开发计划"""
    #获取主键
    id = request.POST.get('id')

    #逻辑删除客户开发计划
    CusDevPlan.objects.filter(pk=id).update(isValid=0, updateDate=datetime.now())

    return JsonResponse({'code': 200, 'msg': '修改成功'})



@csrf_exempt
@require_POST
def update_dev_result(request):
    """开发成功或者开发失败"""
    #接收参数
    saleChanceId = request.POST.get('saleChanceId')
    devResult = request.POST.get('devResult')
    SaleChance.objects.filter(pk=saleChanceId).update(devResult=devResult, updateDate=datetime.now())

    return JsonResponse({'code': 200, 'msg': '操作成功'})






































