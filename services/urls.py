from django.urls import path
from . import views

urlpatterns = [
    path('', views.services_list, name='services'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),
]
