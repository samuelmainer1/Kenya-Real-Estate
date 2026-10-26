from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ManagedPropertyViewSet, MaintenanceScheduleViewSet,
    TenantViewSet, RentPaymentViewSet
)

router = DefaultRouter()
router.register(r'properties', ManagedPropertyViewSet, basename='api-property')
router.register(r'maintenance', MaintenanceScheduleViewSet, basename='api-maintenance')
router.register(r'tenants', TenantViewSet, basename='api-tenant')
router.register(r'rent-payments', RentPaymentViewSet, basename='api-rent-payment')

urlpatterns = [
    path('', include(router.urls)),
]

