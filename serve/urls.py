from django.urls import path
from serve import views



#设置命令空间名称
app_name='serve'

urlpatterns = [
    #服务创建
    path('<str:template>/index/', views.serve_index, name='serve_index'),
    path('list/',views.select_serve_list,name='select_serve_list'),
    #服务创建---添加
    path('<str:template>/workflow/', views.serve_workflow,name='serve_workflow'),
    path('create/', views.create_serve, name='create_serve'),
    #服务分配
    path('update/', views.update_serve, name='update_serve'),


]