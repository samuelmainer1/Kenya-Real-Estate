from django.contrib import admin, messages
from .models import Listing, Booking, ListingSubscription
from .forms import ListingAdminForm

class ListingAdmin(admin.ModelAdmin):
    form = ListingAdminForm
    list_display = ('id', 'title', 'property_type', 'is_published', 'realtor_verified', 'price', 'list_date', 'realtor', 'city', 'state')
    list_display_links = ('id', 'title')
    list_filter = ('property_type', 'realtor', 'realtor__is_verified', 'city', 'state', 'is_published', 'bedrooms', 'bathrooms')
    search_fields = ('title', 'description', 'address', 'city', 'state', 'zipcode', 'price')
    list_per_page = 25

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'property_type', 'description', 'realtor', 'is_published', 'list_date'),
            'description': 'Leave the slug blank to auto-generate it from the title. Duplicate titles are allowed; the URL slug is made unique automatically.'
        }),
        ('Location Details', {
            'fields': ('address', 'city', 'state', 'zipcode', 'latitude', 'longitude'),
            'description': 'Enter the property location details. Coordinates are optional but help with map display.'
        }),
        ('Property Details', {
            'fields': ('price', 'bedrooms', 'bathrooms', 'garage', 'sqft', 'lot_size'),
            'description': 'Enter the property specifications and pricing information.'
        }),
        ('Photos', {
            'fields': ('photo_main', 'photo_1', 'photo_2', 'photo_3', 'photo_4', 'photo_5', 'photo_6'),
            'classes': ('collapse',),
            'description': 'Upload property photos. The main photo is required and will be the primary display image.'
        }),
        ('Amenities & Features', {
            'fields': ('amenities',),
            'classes': ('collapse',),
            'description': 'List nearby amenities and features. Enter each amenity on a new line.'
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/amenities-admin.css',)
        }
        js = ('admin/js/amenities-admin.js',)

    def realtor_verified(self, obj):
        return obj.realtor.is_verified

    realtor_verified.boolean = True
    realtor_verified.short_description = 'Realtor verified'

    def save_model(self, request, obj, form, change):
        if obj.is_published and obj.realtor_id and not obj.realtor.is_verified:
            self.message_user(
                request,
                'Listing saved as unpublished because the assigned realtor is not verified yet.',
                messages.WARNING,
            )
            obj.is_published = False
        super().save_model(request, obj, form, change)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'get_booking_type', 'client', 'client_email', 'get_booking_period', 'status', 'created_at')
    list_filter = ('booking_type', 'status', 'created_at')
    search_fields = ('listing__title', 'client__username', 'client_email', 'client_phone')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'get_booking_details')

    fieldsets = (
        ('Booking Information', {
            'fields': ('listing', 'booking_type', 'client', 'client_email', 'client_phone', 'status', 'created_at')
        }),
        ('Viewing Details', {
            'fields': ('date', 'time'),
            'classes': ('collapse',),
        }),
        ('Airbnb Details', {
            'fields': ('check_in_date', 'check_out_date', 'check_in_time', 'check_out_time'),
            'classes': ('collapse',),
        }),
    )

    def get_booking_type(self, obj):
        """Display booking type with icon"""
        if obj.booking_type == 'airbnb':
            return '🏨 Airbnb Booking'
        return '👁️ Property Viewing'
    get_booking_type.short_description = 'Booking Type'

    def get_booking_period(self, obj):
        """Display booking period based on type"""
        if obj.booking_type == 'airbnb':
            return f"{obj.check_in_date} to {obj.check_out_date}"
        return f"{obj.date} at {obj.time}"
    get_booking_period.short_description = 'Period'

    def get_booking_details(self, obj):
        """Display detailed booking information"""
        if obj.booking_type == 'airbnb':
            return f"Check-in: {obj.check_in_date} at {obj.check_in_time}\nCheck-out: {obj.check_out_date} at {obj.check_out_time}"
        return f"Date: {obj.date}\nTime: {obj.time}"
    get_booking_details.short_description = 'Booking Details'

@admin.register(ListingSubscription)
class ListingSubscriptionAdmin(admin.ModelAdmin):
    """Property-alert subscribers (was previously not reachable in the admin)."""

    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    ordering = ('-subscribed_at',)
    list_per_page = 50
    readonly_fields = ('unsubscribe_token', 'subscribed_at')
    actions = ('mark_active', 'mark_inactive')

    @admin.action(description='Re-activate selected subscribers')
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriber(s) re-activated.', messages.SUCCESS)

    @admin.action(description='Deactivate selected subscribers')
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriber(s) deactivated.', messages.SUCCESS)


admin.site.register(Listing, ListingAdmin)
admin.site.register(Booking, BookingAdmin)

