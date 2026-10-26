"""User and role management.

``django.contrib.auth`` is installed but its models were never registered, so
the site owner could not create staff accounts, change passwords, or assign
roles from ``/admin/``. That is the single most important requirement for
"control everything", so both models are registered with the stock Django
forms (which hash passwords correctly) plus a few UX additions.
"""

from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html

from listings.models import Booking
from testimonials.models import Testimonial

# ``django.contrib.auth.admin`` registers User and Group with stock admins as
# soon as it is imported. Replace them with the versions below instead of
# raising AlreadyRegistered. is_registered() keeps this idempotent.
for _model in (User, Group):
    if admin.site.is_registered(_model):
        admin.site.unregister(_model)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Stock Django user admin, extended with site-activity columns."""

    list_display = ('username', 'email', 'full_name', 'role', 'is_active', 'date_joined')
    list_display_links = ('username', 'email')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    list_per_page = 25
    readonly_fields = ('last_login', 'date_joined', 'activity_summary')

    # Keep the stock fieldsets, then append an activity panel.
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Site activity', {
            'fields': ('activity_summary',),
            'classes': ('collapse',),
            'description': 'Bookings and reviews submitted by this account.',
        }),
    )

    @admin.display(description='Name', ordering='first_name')
    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip() or '—'

    @admin.display(description='Role')
    def role(self, obj):
        if obj.is_superuser:
            label, colour = 'Superuser', '#10284e'
        elif obj.is_staff:
            label, colour = 'Staff', '#0f766e'
        else:
            label, colour = 'Client', '#475569'
        return format_html(
            '<span style="display:inline-block;padding:1px 8px;border-radius:10px;'
            'font-size:11px;font-weight:600;background:{}1a;color:{};">{}</span>',
            colour, colour, label,
        )

    @admin.display(description='Activity')
    def activity_summary(self, obj):
        bookings = Booking.objects.filter(client=obj).count()
        reviews = Testimonial.objects.filter(client=obj).count()
        return f'{bookings} booking(s), {reviews} testimonial(s)'


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    """Roles. Permissions assigned here control what staff can reach."""

