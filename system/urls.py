
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
    path('role/create_or_update/',views.role_create_or_update,name='role_create_or_update'),
    path('role/create/',views.create_role,name='create_role'),
    path('role/update/',views.update_role,name='update_role'),
    #角色管理--授权
    path('role/grant/',views.role_grant,name='role_grant'),
    path('role/module/',views.select_role_module,name='select_role_module'),
    path('role/grant/add/',views.role_relate_module,name='role_relate_module'),
    #用户管理--查询用户
    path('user/',views.user_index, name='user_index'),
    path('user/list/',views.select_user,name='select_user'),
    #用户管理--添加用户
    path('user/create_or_update/',views.user_create_or_update,name='user_create_or_update'),
    path('user/role/',views.select_role_for_user,name='select_role_for_user'),
    path('user/create/',views.create_user, name='create_user'),
    path('user/update/',views.update_user, name='update_user'),
    path('user/delete/',views.delete_user, name='delete_user'),
    #


    #
    path('init/', views.index_init,name='index_init'),



]