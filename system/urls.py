
from  django.urls import path

from . import views

#设置命名空间
app_name = 'system'

urlpatterns = [
    path('', views.login, name='login'),
    path('registry/',views.registry, name='registry'),
    # path('unique_username/', views.unique_username, name='unique_username'),
    path('unique_username/', views.unique_username, name='unique_username'),
    path('captcha/', views.generate_captcha, name='captcha'),
]