from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import ListView, DetailView
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import ManagedProperty, MaintenanceSchedule, Tenant, RentPayment
from listings.models import Listing

def property_management(request):
    """
    Display all properties under management
    """
    managed_properties = ManagedProperty.objects.select_related('listing').filter(
        management_status='active'
    ).order_by('-management_start_date')

    # Get filter parameters
    occupancy_filter = request.GET.get('occupancy', '')
    maintenance_filter = request.GET.get('maintenance', '')

    if occupancy_filter:
        managed_properties = managed_properties.filter(occupancy_status=occupancy_filter)

    if maintenance_filter == 'true':
        managed_properties = managed_properties.filter(maintenance_required=True)

    context = {
        'managed_properties': managed_properties,
        'occupancy_filter': occupancy_filter,
        'maintenance_filter': maintenance_filter,
    }

    return render(request, 'property_management/property_management.html', context)

def managed_property_detail(request, pk):
    """
    Display detailed information about a managed property
    """
    managed_property = get_object_or_404(
        ManagedProperty.objects.select_related('listing'), pk=pk
    )
    tenants = managed_property.tenants.filter(status='active')
    maintenance_schedules = managed_property.maintenance_schedules.filter(status__in=['scheduled', 'in_progress'])

    context = {
        'managed_property': managed_property,
        'listing': managed_property.listing,
        'tenants': tenants,
        'maintenance_schedules': maintenance_schedules,
    }

    return render(request, 'property_management/managed_property_detail.html', context)

@staff_member_required
def analytics_dashboard(request):
    """
    Display analytics and reports dashboard

    Staff-only: this page aggregates portfolio value, rent collected and
    arrears across every managed property, so it is business data rather than
    marketing content. Anonymous visitors are redirected to the admin login and
    non-staff users are refused, matching the rest of the reporting surface.
    """
    # Get all managed properties
    all_properties = ManagedProperty.objects.select_related('listing')
    active_properties = all_properties.filter(management_status='active')

    # Property Statistics
    total_properties = all_properties.count()
    active_count = active_properties.count()
    occupied_count = active_properties.filter(occupancy_status='occupied').count()
    vacant_count = active_properties.filter(occupancy_status='vacant').count()
    under_maintenance_count = active_properties.filter(occupancy_status='under_maintenance').count()

    # Tenant Statistics
    total_tenants = Tenant.objects.filter(status='active').count()
    total_active_leases = Tenant.objects.filter(status='active', lease_end_date__gte=timezone.now().date()).count()

    # Rent Statistics
    total_rent_due = RentPayment.objects.filter(status__in=['pending', 'overdue']).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    total_rent_collected = RentPayment.objects.filter(status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    overdue_payments = RentPayment.objects.filter(status='overdue').count()

    # Maintenance Statistics
    total_maintenance = MaintenanceSchedule.objects.count()
    completed_maintenance = MaintenanceSchedule.objects.filter(status='completed').count()
    pending_maintenance = MaintenanceSchedule.objects.filter(status__in=['scheduled', 'in_progress']).count()
    overdue_maintenance = MaintenanceSchedule.objects.filter(
        status__in=['scheduled', 'in_progress'],
        scheduled_date__lt=timezone.now().date()
    ).count()

    # Recent maintenance
    recent_maintenance = MaintenanceSchedule.objects.select_related('managed_property').order_by('-scheduled_date')[:5]

    # Upcoming maintenance (next 7 days)
    today = timezone.now().date()
    upcoming_maintenance = MaintenanceSchedule.objects.filter(
        status__in=['scheduled', 'in_progress'],
        scheduled_date__gte=today,
        scheduled_date__lte=today + timedelta(days=7)
    ).count()

    # Overdue rent payments
    overdue_rent = RentPayment.objects.filter(status='overdue').select_related('tenant')[:5]

    # Property occupancy rate
    occupancy_rate = (occupied_count / active_count * 100) if active_count > 0 else 0

    # Monthly rent collection rate
    total_monthly_rent = Tenant.objects.filter(status='active').aggregate(Sum('monthly_rent'))['monthly_rent__sum'] or 0

    context = {
        'total_properties': total_properties,
        'active_count': active_count,
        'occupied_count': occupied_count,
        'vacant_count': vacant_count,
        'under_maintenance_count': under_maintenance_count,
        'total_tenants': total_tenants,
        'total_active_leases': total_active_leases,
        'total_rent_due': total_rent_due,
        'total_rent_collected': total_rent_collected,
        'overdue_payments': overdue_payments,
        'total_maintenance': total_maintenance,
        'completed_maintenance': completed_maintenance,
        'pending_maintenance': pending_maintenance,
        'overdue_maintenance': overdue_maintenance,
        'recent_maintenance': recent_maintenance,
        'upcoming_maintenance': upcoming_maintenance,
        'overdue_rent': overdue_rent,
        'occupancy_rate': round(occupancy_rate, 2),
        'total_monthly_rent': total_monthly_rent,
    }

    return render(request, 'property_management/analytics_dashboard.html', context)

@staff_member_required
def tenant_list(request):
    """
    Display list of all tenants

    Staff-only: the register contains tenant names, contacts and lease terms.
    """
    tenants = Tenant.objects.select_related('managed_property').order_by('-move_in_date')

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        tenants = tenants.filter(status=status_filter)

    # Filter by property
    property_filter = request.GET.get('property', '')
    if property_filter:
        tenants = tenants.filter(managed_property_id=property_filter)

    # Get all properties for filter dropdown
    properties = ManagedProperty.objects.select_related('listing')

    context = {
        'tenants': tenants,
        'properties': properties,
        'status_filter': status_filter,
        'property_filter': property_filter,
    }

    return render(request, 'property_management/tenant_list.html', context)

@staff_member_required
def tenant_detail(request, pk):
    """
    Display detailed information about a tenant
    """
    tenant = get_object_or_404(
        Tenant.objects.select_related('managed_property'), pk=pk
    )
    rent_payments = tenant.rent_payments.order_by('-due_date')

    context = {
        'tenant': tenant,
        'rent_payments': rent_payments,
    }

    return render(request, 'property_management/tenant_detail.html', context)

@staff_member_required
def maintenance_list(request):
    """
    Display list of all maintenance schedules

    Staff-only: schedules reference tenants and property internals.
    """
    maintenance = MaintenanceSchedule.objects.select_related('managed_property').order_by('scheduled_date')

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        maintenance = maintenance.filter(status=status_filter)

    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        maintenance = maintenance.filter(priority=priority_filter)

    context = {
        'maintenance': maintenance,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }

    return render(request, 'property_management/maintenance_list.html', context)

@staff_member_required
def rent_payments_list(request):
    """
    Display list of all rent payments

    Staff-only: this is per-tenant financial data.
    """
    payments = RentPayment.objects.select_related('tenant').order_by('-due_date')

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        payments = payments.filter(status=status_filter)

    context = {
        'payments': payments,
        'status_filter': status_filter,
    }

    return render(request, 'property_management/rent_payments_list.html', context)
