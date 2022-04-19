
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
]