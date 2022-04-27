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


]