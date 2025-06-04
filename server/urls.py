from django.urls import path

from server import views

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
]
