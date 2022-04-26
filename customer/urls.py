from  django.urls import path

from customer import views

app_name = 'customer'

urlpatterns = [
    path('index/', views.customer_index, name='customer_index'),
    path('list/',views.select_customer_list, name='select_customer_list'),
]