from django.conf import settings
from services.models import Service
from legal.models import SEOSettings

SITE_NAME = getattr(settings, 'SITE_NAME', 'Kenya Realestate Platform')
SITE_TAGLINE = getattr(settings, 'SITE_TAGLINE', 'Premium Real Estate in Kenya')
SITE_DESCRIPTION = getattr(settings, 'SITE_DESCRIPTION', "Kenya's premier real estate platform")
SITE_KEYWORDS = getattr(settings, 'SITE_KEYWORDS', 'real estate Kenya, property Kenya')


def _site_url():
    """Read SITE_URL at call time so overrides/env changes are picked up."""
    return getattr(settings, 'SITE_URL', '').rstrip('/')


def _canonical_path(request):
    """Return the canonical path for a request, keeping the trailing slash.

    Django's APPEND_SLASH redirects ``/listings`` -> ``/listings/``, so the
    trailing-slash form is the real URL. Canonical tags must match it exactly,
    otherwise every canonical points at a redirect.
    """
    path = request.path
    if path != '/' and not path.endswith('/'):
        path = path + '/'
    return path


def global_context(request):
    """Add global context variables"""
    try:
        seo_settings = SEOSettings.objects.first()
    except Exception:
        seo_settings = None

    # Site-wide settings edited in the Control Centre, cached for an hour and
    # invalidated on save. Any failure falls back to the settings.py values so
    # the public site never 500s over an unmigrated settings table.
    try:
        from core.models import GlobalSettings

        global_settings = GlobalSettings.load()
    except Exception:
        global_settings = None

    site_name = seo_settings.site_name if seo_settings and seo_settings.site_name else SITE_NAME
    site_tagline = SITE_TAGLINE
    contact_phone = contact_email = None
    announcement = None
    if global_settings is not None:
        site_name = global_settings.display_name
        site_tagline = global_settings.display_tagline or SITE_TAGLINE
        contact_phone = global_settings.phone or None
        contact_email = global_settings.email or None
        if global_settings.announcement_active and global_settings.announcement:
            announcement = global_settings.announcement

    site_description = seo_settings.site_description if seo_settings and seo_settings.site_description else SITE_DESCRIPTION
    site_keywords = seo_settings.site_keywords if seo_settings and seo_settings.site_keywords else SITE_KEYWORDS

    site_origin = (_site_url() or request.build_absolute_uri('/').rstrip('/')).rstrip('/')

    return {
        'featured_services': Service.objects.filter(is_featured=True, is_active=True).order_by('order')[:5],
        'seo_settings': seo_settings,
        'global_settings': global_settings,
        'site_announcement': announcement,
        'contact_phone': contact_phone,
        'contact_email': contact_email,
        'site_name': site_name,
        'site_tagline': site_tagline,
        'site_description': site_description,
        'site_keywords': site_keywords,
        'site_url': site_origin,
        'canonical_url': site_origin + _canonical_path(request),
    }
