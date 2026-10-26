from django.db import models
from listings.models import Listing
from django.utils import timezone
from django.contrib.auth.models import User

class ManagedProperty(models.Model):
    """
    Model to track properties under management.
    Links to existing Listing model and adds management-specific information.
    """
    MANAGEMENT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='managed_property')
    management_status = models.CharField(
        max_length=20,
        choices=MANAGEMENT_STATUS_CHOICES,
        default='active',
        help_text='Current management status of the property'
    )
    management_start_date = models.DateField(default=timezone.now)
    management_end_date = models.DateField(null=True, blank=True)
    management_notes = models.TextField(blank=True, help_text='Internal notes about property management')
    maintenance_required = models.BooleanField(default=False)
    maintenance_notes = models.TextField(blank=True, help_text='Maintenance requirements or issues')
    occupancy_status = models.CharField(
        max_length=20,
        choices=[
            ('occupied', 'Occupied'),
            ('vacant', 'Vacant'),
            ('under_maintenance', 'Under Maintenance'),
        ],
        default='vacant'
    )
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-management_start_date']
        verbose_name = 'Managed Property'
        verbose_name_plural = 'Managed Properties'

    def __str__(self):
        return f"{self.listing.title} - {self.get_management_status_display()}"

    def is_active(self):
        """Check if property is currently under active management"""
        return self.management_status == 'active'


class MaintenanceSchedule(models.Model):
    """
    Model to track scheduled maintenance for properties
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    managed_property = models.ForeignKey(ManagedProperty, on_delete=models.CASCADE, related_name='maintenance_schedules')
    title = models.CharField(max_length=200, help_text='Maintenance task title')
    description = models.TextField(help_text='Detailed description of maintenance work')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    estimated_duration = models.CharField(max_length=100, blank=True, help_text='e.g., 2 hours, 1 day')
    completion_date = models.DateField(null=True, blank=True)
    completion_notes = models.TextField(blank=True, help_text='Notes on completed maintenance')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_tasks')
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']
        verbose_name = 'Maintenance Schedule'
        verbose_name_plural = 'Maintenance Schedules'

    def __str__(self):
        return f"{self.title} - {self.managed_property.listing.title}"

    def is_overdue(self):
        """Check if maintenance is overdue"""
        if self.status == 'completed' or self.status == 'cancelled':
            return False
        return timezone.now().date() > self.scheduled_date


class Tenant(models.Model):
    """
    Model to track tenants in managed properties
    """
    TENANT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('evicted', 'Evicted'),
        ('moved_out', 'Moved Out'),
    ]

    managed_property = models.ForeignKey(ManagedProperty, on_delete=models.CASCADE, related_name='tenants')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    national_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=TENANT_STATUS_CHOICES, default='active')
    move_in_date = models.DateField()
    move_out_date = models.DateField(null=True, blank=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    lease_start_date = models.DateField()
    lease_end_date = models.DateField()
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-move_in_date']
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.managed_property.listing.title}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_lease_active(self):
        """Check if lease is currently active"""
        today = timezone.now().date()
        return self.lease_start_date <= today <= self.lease_end_date


class RentPayment(models.Model):
    """
    Model to track rent payments from tenants
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('overdue', 'Overdue'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='rent_payments')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    payment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date']
        verbose_name = 'Rent Payment'
        verbose_name_plural = 'Rent Payments'

    def __str__(self):
        return f"Rent - {self.tenant.get_full_name()} - {self.due_date}"

    def is_overdue(self):
        """Check if payment is overdue"""
        if self.status == 'paid':
            return False
        return timezone.now().date() > self.due_date
