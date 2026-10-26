from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import btre.admin_site  # noqa: F401  (admin branding + audit log)
import btre.admin_dashboard  # noqa: F401  (custom /admin/ index)

from legal.views import privacy_policy, terms_of_service, sitemap_xml, robots_txt

urlpatterns = [
    path('', include('pages.urls')),
    path('listings/', include('listings.urls')),
    path('accounts/', include('accounts.urls')),
    path('contacts/', include('contacts.urls')),
    path('blog/', include('blog.urls')),
    path('services/', include('services.urls')),
    path('testimonials/', include('testimonials.urls')),
    path('property-management/', include('property_management.urls')),
    path('api/property-management/', include('property_management.api_urls')),

    # Public legal pages (single source of truth - also linked from the footer)
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('terms-of-service/', terms_of_service, name='terms_of_service'),
    path('legal/', include('legal.urls')),

    # SEO
    path('sitemap.xml', sitemap_xml, name='sitemap'),
    path('robots.txt', robots_txt, name='robots'),

    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Branded error pages (see btre/views.py). Works with DEBUG on or off.
handler404 = 'btre.views.page_not_found'
handler500 = 'btre.views.server_error'
