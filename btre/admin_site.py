"""Branding and chrome for the Django admin ("Control Centre").

Django reads ``site_header`` / ``site_title`` / ``index_title`` from the
``AdminSite`` object, so setting them here gives every admin page (login,
changelists, change forms) consistent branding without any override templates.

``each_context`` is also wrapped so every admin page receives the grouped
Control Centre navigation (see ``btre/nav_sidebar.py``). Doing it here rather
than in each ``ModelAdmin`` means a newly registered model shows up in the
sidebar with no extra wiring.

Note on ``site_name``: the admin context does **not** define it - like every
Django template, ``{{ site_name }}`` resolves to the host name there (e.g.
``127.0.0.1``). Admin templates must therefore use ``kc_site_name``, which is
branded and falls back to ``settings.SITE_NAME``.

Colours are handled by ``btre/static/css/admin-control.css``. Prefer CSS
overrides over overriding ``admin/base_site.html``: the admin's own dark-mode
support lives in ``base.css``, and a brand-blue ``#header`` rule would then
paint white text on a white header for dark-mode users.
"""

from django.conf import settings
from django.contrib import admin

admin.site.site_header = 'Kenya Realestate Platform'
admin.site.site_title = 'Kenya Realestate Admin'
admin.site.index_title = 'Control Centre'

# The Control Centre navigation is registered on every admin page through the
# ``each_context`` wrapper below, so the stock app-list sidebar stays enabled.
admin.site.enable_nav_sidebar = True


def _brand_name():
    """The site's display name, editable in the Control Centre."""
    try:
        from core.models import GlobalSettings

        return GlobalSettings.load().display_name
    except Exception:  # noqa: BLE001 - branding must never break the admin
        return getattr(settings, 'SITE_NAME', 'Kenya Realestate Platform')


def _install_sidebar_context():
    """Merge the Control Centre navigation into every admin page's context."""
    from btre.nav_sidebar import sidebar_context

    # ``admin.site`` is a ``LazyObject``; reading ``.each_context`` off it would
    # hand back an *unbound* function (``self`` missing) and silently return the
    # bare class dict. Force initialisation and call it bound instead.
    site = admin.site._wrapped if admin.site._wrapped is not None else admin.site
    original = site.each_context

    def each_context(request):
        # ``each_context`` already contains ``available_apps`` for this user,
        # so building the nav from the returned dict keeps permissions exact
        # and costs no extra queries beyond the badge counts.
        context = sidebar_context(request, original(request))
        context['kc_site_name'] = _brand_name()
        return context

    site.each_context = each_context


_install_sidebar_context()



def _register_audit_log():
    """Expose Django's ``LogEntry`` as a read-only audit trail.

    ``LogEntry`` is not registered by default, so admins cannot see who
    changed or deleted what. It is deliberately read-only: the log is written
    by the admin itself, and editing it would destroy its value as a record.
    """
    from django.contrib.admin.models import LogEntry

    class LogEntryAdmin(admin.ModelAdmin):
        list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
        list_filter = ('action_flag', 'content_type', 'user')
        search_fields = ('object_repr', 'change_message')
        date_hierarchy = 'action_time'
        ordering = ('-action_time',)
        list_per_page = 50

        def has_add_permission(self, request):
            return False

        def has_change_permission(self, request, obj=None):
            return False

        def has_delete_permission(self, request, obj=None):
            return False

    admin.site.register(LogEntry, LogEntryAdmin)


_register_audit_log()

