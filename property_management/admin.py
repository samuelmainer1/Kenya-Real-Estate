from django.contrib import admin
from .models import ManagedProperty, MaintenanceSchedule, Tenant, RentPayment

@admin.register(ManagedProperty)
class ManagedPropertyAdmin(admin.ModelAdmin):
    list_display = ('listing_title', 'management_status', 'occupancy_status', 'management_start_date', 'maintenance_required', 'last_inspection_date')
    list_filter = ('management_status', 'occupancy_status', 'maintenance_required', 'management_start_date')
    search_fields = ('listing__title', 'listing__address', 'listing__city')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('management_status', 'occupancy_status', 'maintenance_required')
    list_per_page = 25

    fieldsets = (
        ('Property Information', {
            'fields': ('listing',)
        }),
        ('Management Details', {
            'fields': ('management_status', 'management_start_date', 'management_end_date', 'management_notes')
        }),
        ('Occupancy & Maintenance', {
            'fields': ('occupancy_status', 'maintenance_required', 'maintenance_notes')
        }),
        ('Inspections', {
            'fields': ('last_inspection_date', 'next_inspection_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def listing_title(self, obj):
        return obj.listing.title
    listing_title.short_description = 'Property'


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_name', 'priority', 'status', 'scheduled_date', 'is_overdue_display', 'assigned_to', 'cost')
    list_filter = ('priority', 'status', 'scheduled_date', 'managed_property')
    search_fields = ('title', 'description', 'managed_property__listing__title')
    readonly_fields = ('created_at', 'updated_at', 'is_overdue_display')
    list_editable = ('status', 'priority')
    list_per_page = 25

    fieldsets = (
        ('Maintenance Details', {
            'fields': ('managed_property', 'title', 'description', 'priority', 'status')
        }),
        ('Schedule', {
            'fields': ('scheduled_date', 'scheduled_time', 'estimated_duration')
        }),
        ('Assignment & Cost', {
            'fields': ('assigned_to', 'cost')
        }),
        ('Completion', {
            'fields': ('completion_date', 'completion_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def property_name(self, obj):
        return obj.managed_property.listing.title
    property_name.short_description = 'Property'

    def is_overdue_display(self, obj):
        return obj.is_overdue()
    is_overdue_display.short_description = 'Overdue'
    is_overdue_display.boolean = True


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'property_name', 'status', 'move_in_date', 'lease_end_date', 'monthly_rent', 'is_lease_active_display')
    list_filter = ('status', 'move_in_date', 'managed_property')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'national_id', 'managed_property__listing__title')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    list_per_page = 25

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'national_id')
        }),
        ('Property & Status', {
            'fields': ('managed_property', 'status', 'move_in_date', 'move_out_date')
        }),
        ('Lease Information', {
            'fields': ('lease_start_date', 'lease_end_date', 'monthly_rent', 'deposit_amount')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def property_name(self, obj):
        return obj.managed_property.listing.title
    property_name.short_description = 'Property'

    def is_lease_active_display(self, obj):
        return obj.is_lease_active()
    is_lease_active_display.short_description = 'Lease Active'
    is_lease_active_display.boolean = True


@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ('tenant_name', 'amount_due', 'amount_paid', 'due_date', 'status', 'is_overdue_display', 'payment_method')
    list_filter = ('status', 'due_date', 'payment_method', 'tenant__managed_property')
    search_fields = ('tenant__first_name', 'tenant__last_name', 'reference_number')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'payment_method')
    list_per_page = 25

    fieldsets = (
        ('Tenant & Amount', {
            'fields': ('tenant', 'amount_due', 'amount_paid')
        }),
        ('Payment Details', {
            'fields': ('due_date', 'payment_date', 'status', 'payment_method', 'reference_number')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def tenant_name(self, obj):
        return obj.tenant.get_full_name()
    tenant_name.short_description = 'Tenant'

    def is_overdue_display(self, obj):
        return obj.is_overdue()
    is_overdue_display.short_description = 'Overdue'
    is_overdue_display.boolean = True
