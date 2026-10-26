"""Admin for site-wide settings.

The admin model is deliberately a single settings form rather than a list: there
is exactly one settings row, so the changelist redirects straight to its change
form and the add/delete buttons are hidden. That avoids the confusing "table
with one row" experience the default admin would give.
"""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from core.models import GlobalSettings


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Identity', {
            'fields': ('site_name', 'site_tagline'),
            'description': 'Leave a field blank to fall back to the value in settings.py.',
        }),
        ('Contact details', {
            'fields': ('phone', 'whatsapp_number', 'email', 'physical_address', 'office_hours'),
        }),
        ('Social profiles', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url'),
        }),
        ('Site-wide announcement', {
            'fields': ('announcement_active', 'announcement'),
            'description': 'Shown as a banner across the public site while "active" is ticked.',
        }),
    )
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # One row only. Once it exists the changelist link opens the form, so
        # an "Add" button would just create confusion (save() forces pk=1).
        return not GlobalSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        """Open the single settings form instead of a one-row table."""
        if not request.GET and self.has_view_permission(request):
            obj = GlobalSettings.load()
            return HttpResponseRedirect(
                reverse('admin:core_globalsettings_change', args=[obj.pk])
            )
        return super().changelist_view(request, extra_context)

