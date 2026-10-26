from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from .models import LegalPage, Sitemap
from listings.models import Listing
from services.models import Service
from blog.models import Blog


def legal_page(request, slug):
    """Display legal page"""
    page = get_object_or_404(LegalPage, slug=slug, is_active=True)

    context = {
        'page': page,
        'last_updated': page.last_updated,
        'effective_date': page.effective_date,
    }
    return render(request, 'legal/legal_page.html', context)


def privacy_policy(request):
    """Privacy policy shortcut"""
    page = get_object_or_404(LegalPage, page_type='privacy', is_active=True)
    return legal_page(request, page.slug)


def terms_of_service(request):
    """Terms of service shortcut"""
    page = get_object_or_404(LegalPage, page_type='terms', is_active=True)
    return legal_page(request, page.slug)


# Page types that also have a dedicated short URL at the site root. The
# /legal/<slug>/ duplicate must not be promoted in the sitemap, otherwise
# crawlers index the same content twice.
SHORT_URL_NAMES = {
    'privacy': 'privacy_policy',
    'terms': 'terms_of_service',
}


def _site_origin(request):
    """Public origin for absolute URLs in the sitemap.

    Prefers the configured SITE_URL so the output stays correct behind a
    reverse proxy (no internal :80 port leaking into <loc>); falls back to the
    request host in development.
    """
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    if site_url:
        return site_url
    return '{}://{}'.format(request.scheme, request.get_host()).rstrip('/')


def _normalise_custom_url(url):
    """Turn an admin-supplied custom sitemap entry into a valid local path.

    Returns None when the entry cannot be used (empty, or already absolute).
    Handles the common data-entry mistakes: missing leading slash, double
    slashes, and missing trailing slash (which would otherwise cost the crawler
    an extra redirect hop).
    """
    if not url:
        return None
    url = url.strip()
    if url.lower().startswith(('http://', 'https://')):
        return None
    if not url.startswith('/'):
        url = '/' + url
    # Collapse duplicate slashes but keep the leading one.
    while '//' in url:
        url = url.replace('//', '/')
    if url != '/' and not url.endswith('/'):
        url = url + '/'
    return url


def sitemap_xml(request):
    """Generate dynamic XML sitemap"""
    origin = _site_origin(request)

    # Static pages - these must be the exact URLs the router serves
    # (all use a trailing slash, otherwise they 404 or redirect).
    static_urls = [
        {'url': '/', 'priority': '1.0', 'changefreq': 'daily'},
        {'url': '/about/', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/faq/', 'priority': '0.7', 'changefreq': 'monthly'},
        {'url': '/listings/', 'priority': '0.9', 'changefreq': 'daily'},
        {'url': '/services/', 'priority': '0.8', 'changefreq': 'weekly'},
        {'url': '/property-management/', 'priority': '0.8', 'changefreq': 'monthly'},
        {'url': '/blog/', 'priority': '0.7', 'changefreq': 'weekly'},
        {'url': '/testimonials/', 'priority': '0.6', 'changefreq': 'monthly'},
        {'url': '/contacts/', 'priority': '0.8', 'changefreq': 'monthly'},
    ]

    # Dynamic content. Only published listings are exposed (the public()
    # manager also hides listings owned by unverified realtors, which 404).
    # NOTE: photo_main is fetched as a raw string in .values(), so build the
    # media path from settings rather than relying on FieldFile.url.
    media_url = settings.MEDIA_URL or '/media/'
    if not media_url.endswith('/'):
        media_url += '/'

    listings = []
    for row in Listing.objects.public().values('slug', 'list_date', 'photo_main', 'title'):
        photo = row['photo_main']
        listings.append({
            'slug': row['slug'],
            'list_date': row['list_date'],
            'title': row['title'],
            'image_url': (media_url + photo) if photo else None,
        })
    services = Service.objects.filter(is_active=True).values('slug', 'updated_at')
    blogs = Blog.objects.filter(published=True).values('slug', 'posted_at')
    legal_pages = LegalPage.objects.filter(is_active=True).values(
        'slug', 'last_updated', 'page_type')

    # Custom sitemap entries from the admin - normalised and de-duplicated.
    seen = {item['url'] for item in static_urls}
    custom_urls = []
    for entry in Sitemap.objects.filter(is_active=True):
        path = _normalise_custom_url(entry.url)
        if not path or path in seen:
            continue
        seen.add(path)
        custom_urls.append({
            'url': path,
            'priority': entry.priority,
            'changefreq': entry.changefreq,
            'last_modified': entry.last_modified,
        })

    # Legal pages: when a page also has a short root URL (/privacy-policy/),
    # list that canonical URL instead of the /legal/<slug>/ duplicate.
    legal_entries = []
    for page in legal_pages:
        url_name = SHORT_URL_NAMES.get(page['page_type'])
        if url_name:
            path = reverse(url_name)
        else:
            path = '/legal/{}/'.format(page['slug'])
        legal_entries.append({'url': path, 'last_modified': page['last_updated']})

    context = {
        'origin': origin,
        'static_urls': static_urls,
        'listings': listings,
        'services': services,
        'blogs': blogs,
        'legal_entries': legal_entries,
        'custom_urls': custom_urls,
    }

    xml_content = render_to_string('legal/sitemap.xml', context)
    return HttpResponse(xml_content, content_type='application/xml')


def robots_txt(request):
    """Generate robots.txt"""
    # Build the sitemap URL from the configured public origin. Using
    # request.build_absolute_uri() would leak the internal port (e.g. ":80")
    # when running behind a reverse proxy.
    site_url = getattr(settings, 'SITE_URL', '').rstrip('/')
    sitemap_url = f'{site_url}/sitemap.xml' if site_url else request.build_absolute_uri('/sitemap.xml')

    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        "# Disallow admin and private areas",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "",
        f"Sitemap: {sitemap_url}",
    ]

    return HttpResponse('\n'.join(lines), content_type='text/plain')