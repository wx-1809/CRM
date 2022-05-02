from django.urls import path

from report import views

app_name = 'report'

urlpatterns =[
    #客户贡献分析
    path('<str:template>/index/', views.report_index, name='report_index'),
    path('contribute/',views.select_contribute, name='select_contribute'),

    #客户构成分析
    path('composition/',views.select_composition, name='select_composition'),

    #客户服务分析
    path('serve/', views.select_serve,name='select_serve'),

    #客户流失分析
    path('loss/', views.select_loss, name='select_loss'),


]