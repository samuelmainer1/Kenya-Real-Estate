from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import ManagedProperty, MaintenanceSchedule, Tenant, RentPayment
from .serializers import (
    ManagedPropertySerializer, MaintenanceScheduleSerializer,
    TenantSerializer, RentPaymentSerializer
)

class ManagedPropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managed properties
    """
    queryset = ManagedProperty.objects.select_related('listing')
    serializer_class = ManagedPropertySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get statistics for all managed properties"""
        total_properties = self.queryset.count()
        active_properties = self.queryset.filter(management_status='active').count()
        occupied = self.queryset.filter(occupancy_status='occupied').count()
        vacant = self.queryset.filter(occupancy_status='vacant').count()
        
        return Response({
            'total_properties': total_properties,
            'active_properties': active_properties,
            'occupied': occupied,
            'vacant': vacant,
        })
    
    @action(detail=True, methods=['get'])
    def tenants(self, request, pk=None):
        """Get all tenants for a specific property"""
        property_obj = self.get_object()
        tenants = property_obj.tenants.all()
        serializer = TenantSerializer(tenants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def maintenance(self, request, pk=None):
        """Get all maintenance schedules for a specific property"""
        property_obj = self.get_object()
        maintenance = property_obj.maintenance_schedules.all()
        serializer = MaintenanceScheduleSerializer(maintenance, many=True)
        return Response(serializer.data)

class MaintenanceScheduleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for maintenance schedules
    """
    queryset = MaintenanceSchedule.objects.select_related('managed_property', 'assigned_to')
    serializer_class = MaintenanceScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending maintenance tasks"""
        pending = self.queryset.filter(status__in=['scheduled', 'in_progress'])
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue maintenance tasks"""
        overdue = self.queryset.filter(
            status__in=['scheduled', 'in_progress'],
            scheduled_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark a maintenance task as completed"""
        maintenance = self.get_object()
        maintenance.status = 'completed'
        maintenance.completion_date = timezone.now().date()
        maintenance.save()
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)

class TenantViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tenants
    """
    queryset = Tenant.objects.select_related('managed_property')
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active tenants"""
        active_tenants = self.queryset.filter(status='active')
        serializer = self.get_serializer(active_tenants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def rent_history(self, request, pk=None):
        """Get rent payment history for a tenant"""
        tenant = self.get_object()
        payments = tenant.rent_payments.all()
        serializer = RentPaymentSerializer(payments, many=True)
        return Response(serializer.data)

class RentPaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for rent payments
    """
    queryset = RentPayment.objects.select_related('tenant')
    serializer_class = RentPaymentSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue rent payments"""
        overdue = self.queryset.filter(status='overdue')
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending rent payments"""
        pending = self.queryset.filter(status__in=['pending', 'partial'])
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a rent payment as paid"""
        payment = self.get_object()
        payment.status = 'paid'
        payment.payment_date = timezone.now().date()
        payment.amount_paid = payment.amount_due
        payment.save()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get rent payment statistics"""
        total_due = self.queryset.filter(status__in=['pending', 'overdue']).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
        total_paid = self.queryset.filter(status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        overdue_count = self.queryset.filter(status='overdue').count()
        
        return Response({
            'total_due': total_due,
            'total_paid': total_paid,
            'overdue_count': overdue_count,
        })

