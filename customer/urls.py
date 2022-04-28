from  django.urls import path

from customer import views

app_name = 'customer'

urlpatterns = [
    path('index/', views.customer_index, name='customer_index'),
    #查询信息
    path('list/',views.select_customer_list, name='select_customer_list'),
    #修改客户信息
    path('create_or_update/',views.create_or_update_customer, name='create_or_update_customer'),
    path('delete/', views.delete_customer,name='delete_customer'),
    #查询订单数量
    path('order/index/',views.order_index, name='order_index'),
    path('order/list/',views.select_orderlist_by_customerid,name='select_orderlist_by_customerid'),
    #订单页面详情跳转
    path('order/detail/index/',views.order_detail_index,name='order_detail_index'),
    path('order/detail/list/',views.select_orderdetaild_by_orderid,name='select_orderdetaild_by_orderid'),
    #客户流失界面
    path('loss/index/', views.loss_index, name='loss_index'),
    path('loss/list/', views.select_loss_list,name='select_loss_list'),
    #添加暂缓/查看详情
    path('loss/detail/index/', views.loss_detail_index, name='loss_detail_index'),
    path('loss/reprieve/list/',views.select_reprieve_by_lossid, name='select_reprieve_by_lossid'),
    #添加/删除/增加相关信息
    path('loss/reprieve/index/', views.reprieve_index,name='reprieve_index'),
    path('loss/reprieve/create/', views.create_reprieve,name='create_reprieve'),
    path('loss/reprieve/update/', views.update_reprieve,name='update_reprieve'),
    path('loss/reprieve/delete/', views.delete_reprieve,name='delete_reprieve'),
    #确认流失
    path('loss/confirm/',views.update_lossreason_by_lossid,name='update_lossreason_by_lossid'),


]