
from  django.urls import path

from . import views

#设置命名空间
app_name = 'system'

urlpatterns = [
    path('',views.index, name='index'),
    path('welcome/',views.welcome, name='welcome'),
    path('login/', views.login, name='login'),
    path('registry/',views.registry, name='registry'),
    path('unique_username/', views.unique_username, name='unique_username'),
    path('captcha/', views.generate_captcha, name='captcha'),
    path('audit_account/',views.audit_account, name='audit_account'),
    path('user_list/',views.select_user_list, name='select_user_list'),
    path('settings/',views.settings,name='settings'),
    path('logout/',views.logout,name='logout'),
    path('password/',views.password,name='password'),
    #权限管理
    path('module/', views.module_index, name='module_index'),
    path('module/list/',views.select_module, name='select_module'),
    #修改/添加菜单
    path('module/create_or_update/',views.module_create_or_update,name='module_create_or_update'),
    path('module/create/',views.create_module, name='create_module'),
    path('module/update/',views.update_module,name='update_module'),
    #删除模块
    path('module/delete',views.delete_module,name='delete_module'),
    #角色管理--查询角色
    path('role/',views.role_index,name='role_index'),
    path('role/list/',views.select_role,name='select_role'),
    #角色管理---修改/添加角色
    path('role/create_or_update/',views.module_create_or_update,name='create_or_update'),
    path('role/create/',views.create_role,name='create_role'),
    path('role/update/',views.update_role,name='update_role'),
    #
    path('init/', views.index_init,name='index_init'),



]