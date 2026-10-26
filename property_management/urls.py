from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_management, name='property_management'),
    path('<int:pk>/', views.managed_property_detail, name='managed_property_detail'),
    path('analytics/dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/<int:pk>/', views.tenant_detail, name='tenant_detail'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('rent-payments/', views.rent_payments_list, name='rent_payments_list'),
]

