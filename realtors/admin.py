from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Realtor


@admin.register(Realtor)
class RealtorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'email',
        'phone',
        'verification_status',
        'is_mvp',
        'hire_date',
        'verified_at',
    )
    list_display_links = ('id', 'name')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('is_verified', 'is_mvp', 'hire_date')
    list_per_page = 25
    readonly_fields = ('is_verified', 'verified_at', 'verified_by', 'verification_status')
    actions = ('verify_realtors', 'revoke_verification')

    fieldsets = (
        ('Profile', {
            'fields': ('name', 'photo', 'description', 'phone', 'email', 'is_mvp', 'hire_date'),
        }),
        ('Verification', {
            'fields': ('verification_status', 'is_verified', 'verified_at', 'verified_by'),
            'description': 'Use the admin actions "Verify selected realtors" or "Revoke verification" to update trust status.',
        }),
    )

    def verification_status(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="color:#15803d;font-weight:600;">&#10003; Verified</span>'
            )
        return format_html(
            '<span style="color:#b45309;font-weight:600;">&#9888; Pending verification</span>'
        )

    verification_status.short_description = 'Status'

    @admin.action(description='Verify selected realtors')
    def verify_realtors(self, request, queryset):
        updated = 0
        for realtor in queryset.filter(is_verified=False):
            realtor.mark_verified(request.user)
            updated += 1
        self.message_user(
            request,
            f'{updated} realtor(s) verified successfully.',
            messages.SUCCESS,
        )

    @admin.action(description='Revoke verification for selected realtors')
    def revoke_verification(self, request, queryset):
        updated = queryset.filter(is_verified=True).update(
            is_verified=False,
            verified_at=None,
            verified_by=None,
        )
        unpublished = 0
        from listings.models import Listing
        for realtor in queryset:
            count = Listing.objects.filter(realtor=realtor, is_published=True).update(is_published=False)
            unpublished += count
        msg = f'Verification revoked for {updated} realtor(s).'
        if unpublished:
            msg += f' {unpublished} listing(s) were unpublished because their realtor is no longer verified.'
        self.message_user(request, msg, messages.WARNING)
