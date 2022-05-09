from django.urls import path

from sales import views

app_name = 'sales'

urlpatterns = [
    path('index/', views.sales_index, name='sales_index'),
    #客户链表信息查询
    path('list/', views.select_sale_chance_list,name='select_sale_chance_list'),
    path('create_or_update/',views.create_or_update_sales,name='create_or_update_sales'),
    path('customer/',views.select_customer, name='select_customer'),
    path('create/',views.create_sale_chance, name='create_sale_chance'),
    path('update/', views.update_sale_chance, name='update_sale_chance'),
    path('delete/', views.delete_sale_chance, name='delete_sale_chance'),
    #客户开发计划列表
    path('cus_dev_plan/index/',views.cus_dev_plan_index, name='cus_dev_plan_index'),
    path('cus_dev_plan/detail/',views.cus_dev_plan_index_detail,name='cus_dev_plan_index_detail'),
    path('cus_dev_plan/list/',views.select_cus_dev_plan_list,name='select_cus_dev_plan_list'),
    # #添加/删除/修改客户计划表
    path('cus_dev_plan/create_or_update/',views.create_or_update_cus_dev_plan,name='create_or_update_cus_dev_plan'),
    path('cus_dev_plan/create/',views.create_cus_dev_plan,name='create_cus_dev_plan'),
    path('cus_dev_plan/update/',views.update_cus_dev_plan,name='update_cus_dev_plan'),
    path('cus_dev_plan/delete/',views.delete_cus_dev_plan,name='delete_cus_dev_plan'),
    #
    path('cus_dev_plan/dev_result/',views.update_dev_result,name='update_dev_result'),

]