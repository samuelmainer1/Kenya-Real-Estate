from rest_framework import serializers
from .models import ManagedProperty, MaintenanceSchedule, Tenant, RentPayment
from listings.models import Listing

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'address', 'city', 'state', 'price', 'bedrooms', 'bathrooms']

class ManagedPropertySerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    
    class Meta:
        model = ManagedProperty
        fields = [
            'id', 'listing', 'management_status', 'occupancy_status',
            'management_start_date', 'management_end_date', 'maintenance_required',
            'last_inspection_date', 'next_inspection_date', 'created_at', 'updated_at'
        ]

class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    managed_property = ManagedPropertySerializer(read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceSchedule
        fields = [
            'id', 'managed_property', 'title', 'description', 'priority', 'status',
            'scheduled_date', 'scheduled_time', 'estimated_duration', 'completion_date',
            'completion_notes', 'assigned_to', 'assigned_to_name', 'cost', 'created_at', 'updated_at'
        ]

class TenantSerializer(serializers.ModelSerializer):
    managed_property = ManagedPropertySerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'managed_property', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'national_id', 'status', 'move_in_date', 'move_out_date',
            'monthly_rent', 'deposit_amount', 'lease_start_date', 'lease_end_date',
            'emergency_contact_name', 'emergency_contact_phone', 'created_at', 'updated_at'
        ]

class RentPaymentSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    
    class Meta:
        model = RentPayment
        fields = [
            'id', 'tenant', 'amount_due', 'amount_paid', 'due_date', 'payment_date',
            'status', 'payment_method', 'reference_number', 'notes', 'created_at', 'updated_at'
        ]

