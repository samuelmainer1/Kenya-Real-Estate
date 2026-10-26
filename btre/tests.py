"""Site-wide smoke tests: every public page renders, bad IDs 404 (never 500),
and canonical/SEO tags point at real, non-redirecting URLs."""
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.template.loader import get_template, render_to_string
from django.urls import reverse


class PublicPagesTest(TestCase):
    """Every page a visitor or crawler can reach must return 200."""

    def test_static_pages_return_200(self):
        paths = [
            '/', '/about/', '/faq/', '/listings/', '/listings/search/', '/services/',
            '/blog/', '/testimonials/', '/property-management/',
            '/accounts/login/', '/accounts/register/',
            '/sitemap.xml', '/robots.txt',
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200, path)

    def test_staff_reports_are_not_public(self):
        """/property-management/ reports must never be readable anonymously.

        The analytics dashboard aggregates portfolio value, rent collected and
        arrears, and the tenant / maintenance / rent-payment pages list people
        and their payment records. All four were previously open to the public.
        """
        paths = [
            '/property-management/analytics/dashboard/',
            '/property-management/tenants/',
            '/property-management/maintenance/',
            '/property-management/rent-payments/',
        ]
        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertNotEqual(response.status_code, 200, path)

    def test_about_accepts_trailing_slash(self):
        """/about/ is advertised in the sitemap and must not 404."""
        self.assertEqual(self.client.get('/about/').status_code, 200)

    def test_no_raw_template_comments_in_html(self):
        """No internal developer notes may reach the rendered HTML.

        A ``{# ... #}`` comment in Django only applies within a single line. If
        it spans lines, the text is not treated as a comment and lands in the
        page - which is how an internal note about meta tags ended up visible
        above the site header on every page. Multi-line notes must use a
        ``comment`` ... ``endcomment`` block instead.

        This checks the rendered output; test_templates_have_no_multiline_line_
        comments checks the templates themselves.
        """
        leaked = [
            'Single source of truth for the description',
            'Branded 404 page',
        ]
        for path in ('/', '/faq/', '/about/'):
            html = self.client.get(path).content.decode()
            for marker in leaked:
                with self.subTest(path=path, marker=marker):
                    self.assertNotIn(marker, html)
            with self.subTest(path=path):
                self.assertNotIn('{#', html)
                self.assertNotIn('#}', html)

        # 404.html extends base.html, so text outside its blocks is discarded by
        # Django anyway. Rendering it directly still guards against a note
        # slipping inside a block later.
        not_found_html = render_to_string('404.html').replace('&quot;', '"')
        self.assertNotIn('Branded 404 page', not_found_html)
        self.assertNotIn('{#', not_found_html)

    def test_templates_have_no_multiline_line_comments(self):
        """Catch the bad pattern at the source, not just on rendered pages.

        Adding a multi-line note above the HEAD tags of base.html leaks the note
        into every page of the site, so this is checked at the source level as
        well: the rendered-output test above can only see the pages it visits.
        """
        open_block = '{' + '% comment %' + '}'
        close_block = '{' + '% endcomment %' + '}'
        for name in ('base.html', '404.html'):
            source = get_template(name).template.source
            for index, line in enumerate(source.splitlines(), start=1):
                # A {# comment must open and close on the same line.
                if line.count('{#') != line.count('#}'):
                    self.fail(
                        name + ':' + str(index) + ' opens a {# comment without '
                        'closing it on the same line. Django only treats {# #} '
                        'as a comment within one line; use a ' + open_block +
                        ' ... ' + close_block + ' block for multi-line notes.'
                    )

    def test_dashboard_requires_login(self):
        response = self.client.get('/accounts/dashboard/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_api_requires_authentication(self):
        response = self.client.get('/api/property-management/properties/')
        self.assertIn(response.status_code, (401, 403))


class BadInput404Test(TestCase):
    """Regression tests: these used to raise 500 with a full traceback."""

    def test_unknown_listing_slug_is_404(self):
        self.assertEqual(self.client.get('/listings/does-not-exist/').status_code, 404)

    def test_unknown_listing_id_is_404(self):
        self.assertEqual(self.client.get('/listings/999999/').status_code, 404)

    def test_unknown_managed_property_is_404(self):
        self.assertEqual(self.client.get('/property-management/999999/').status_code, 404)

    def test_unknown_tenant_is_404(self):
        """A missing tenant 404s *for staff*; anonymously it redirects to login.

        ``tenant_detail`` is staff-only, so an anonymous request for a bogus ID
        is answered with a redirect before the object lookup happens. The 404
        guarantee only applies once the viewer is allowed through.
        """
        self.client.force_login(
            User.objects.create_superuser('audit-staff', 'staff@example.com', 'pw-that-works-123'))
        self.assertEqual(
            self.client.get('/property-management/tenants/999999/').status_code, 404)

    def test_unknown_blog_post_is_404(self):
        self.assertEqual(self.client.get('/blog/does-not-exist/').status_code, 404)

    def test_unknown_service_is_404(self):
        self.assertEqual(self.client.get('/services/does-not-exist/').status_code, 404)


class LegalPagesTest(TestCase):
    """The legal pages are database-driven, so assert on routes not content."""

    def test_legal_urls_are_routable(self):
        from django.urls import resolve
        for path, view in [
            ('/privacy-policy/', 'privacy_policy'),
            ('/terms-of-service/', 'terms_of_service'),
        ]:
            with self.subTest(path=path):
                self.assertEqual(resolve(path).url_name, view)

    def test_legal_pages_render_when_content_exists(self):
        from legal.models import LegalPage

        LegalPage.objects.create(
            page_type='privacy', slug='privacy-policy', title='Privacy Policy',
            content='<p>Privacy</p>',
        )
        LegalPage.objects.create(
            page_type='terms', slug='terms-of-service', title='Terms of Service',
            content='<p>Terms</p>',
        )
        for path in ['/privacy-policy/', '/terms-of-service/',
                     '/legal/privacy-policy/', '/legal/terms-of-service/']:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200, path)


class SeoTest(TestCase):
    @override_settings(SITE_URL='https://example.com')
    def test_canonical_url_matches_served_url(self):
        """The canonical tag must not point at a URL that redirects."""
        for path in ['/', '/about/', '/listings/', '/services/', '/blog/', '/contacts/']:
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertIn(
                    'rel="canonical" href="https://example.com{}"'.format(path), html)

    @override_settings(SITE_URL='https://example.com')
    def test_canonical_url_has_no_double_slash(self):
        html = self.client.get('/listings/').content.decode()
        self.assertNotIn('https://example.com//', html)

    @override_settings(SITE_URL='https://example.com')
    def test_sitemap_urls_all_resolve_without_redirect(self):
        """Every <loc> in the sitemap must return 200 directly."""
        import re
        body = self.client.get('/sitemap.xml').content.decode()
        locs = re.findall(r'<loc>https://example\.com(/[^<]*)</loc>', body)
        self.assertTrue(locs, 'sitemap should contain URLs')
        for loc in locs:
            with self.subTest(loc=loc):
                response = self.client.get(loc)
                self.assertEqual(response.status_code, 200,
                                 '{} returned {}'.format(loc, response.status_code))

    @override_settings(SITE_URL='https://example.com')
    def test_sitemap_includes_all_public_sections(self):
        body = self.client.get('/sitemap.xml').content.decode()
        for path in ['/about/', '/listings/', '/services/', '/blog/',
                     '/property-management/', '/testimonials/', '/contacts/']:
            with self.subTest(path=path):
                self.assertIn('https://example.com' + path, body)

    def test_robots_txt_points_at_sitemap(self):
        body = self.client.get('/robots.txt').content.decode()
        self.assertIn('Sitemap:', body)
        self.assertIn('/sitemap.xml', body)
        self.assertIn('Disallow: /admin/', body)

    @override_settings(SITE_URL='https://example.com')
    def test_robots_txt_has_no_internal_port(self):
        """Behind a proxy the sitemap URL must not leak ':80' / ':443'."""
        body = self.client.get('/robots.txt').content.decode()
        sitemap_line = [ln for ln in body.splitlines() if ln.startswith('Sitemap:')][0]
        self.assertEqual(sitemap_line, 'Sitemap: https://example.com/sitemap.xml')


class NoDuplicateMetaTest(TestCase):
    """A page must expose exactly one of each SEO tag.

    Regression: several templates injected their own <meta name="description">
    through the generic "meta" block, which *adds to* rather than *replaces*
    the one in base.html. Crawlers then saw two descriptions and picked one
    arbitrarily.
    """

    PAGES = ['/', '/about/', '/listings/', '/services/', '/blog/',
             '/testimonials/', '/property-management/', '/contacts/',
             '/listings/search/']

    PATTERNS = {
        'description': r'<meta name="description"',
        'keywords': r'<meta name="keywords"',
        'robots': r'<meta name="robots"',
        'canonical': r'<link rel="canonical"',
        'og:title': r'<meta property="og:title"',
        'og:description': r'<meta property="og:description"',
        'og:url': r'<meta property="og:url"',
    }

    def test_single_tag_per_page(self):
        import re
        for path in self.PAGES:
            html = self.client.get(path).content.decode()
            for label, pattern in self.PATTERNS.items():
                with self.subTest(path=path, tag=label):
                    found = len(re.findall(pattern, html))
                    self.assertEqual(found, 1,
                                     '{} has {} x {}'.format(path, found, label))

    def test_title_is_clean(self):
        """No leading pipe, no stray whitespace, never empty."""
        import re
        for path in self.PAGES:
            html = self.client.get(path).content.decode()
            with self.subTest(path=path):
                title = re.search(r'<title>(.*?)</title>', html).group(1)
                self.assertTrue(title.strip(), 'empty <title> on ' + path)
                self.assertFalse(title.startswith('|'), 'leading pipe: ' + title)
                self.assertFalse(title.startswith(' '), 'leading space: ' + title)
                self.assertFalse(title.endswith(' '), 'trailing space: ' + title)

    def test_search_results_are_not_indexed(self):
        """Search result pages are thin/duplicate content."""
        html = self.client.get('/listings/search/').content.decode()
        self.assertIn('noindex', html)


class Branded404Test(TestCase):
    """Missing pages must render the branded 404 with a real 404 status."""

    PATHS = ['/nope/', '/listings/does-not-exist/', '/blog/x/y/',
             '/property-management/999999/']

    def test_status_is_404_not_200(self):
        for path in self.PATHS:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 404)

    def test_page_is_branded_and_noindex(self):
        for path in self.PATHS:
            with self.subTest(path=path):
                html = self.client.get(path).content.decode()
                self.assertIn('error-page', html)
                self.assertIn('Page Not Found', html)
                self.assertIn('noindex', html)
                # Must offer a way back, not a dead end.
                self.assertIn('href="/listings/"', html)
                self.assertIn('href="/"', html)

    def test_no_traceback_leaked(self):
        html = self.client.get('/nope/').content.decode()
        self.assertNotIn('Traceback', html)
        self.assertNotIn('URLconf', html)


class SitemapQualityTest(TestCase):
    """Sitemap entries must be clean, unique and resolvable."""

    @override_settings(SITE_URL='https://example.com')
    def test_no_duplicate_locs(self):
        import re
        body = self.client.get('/sitemap.xml').content.decode()
        locs = re.findall(r'<loc>([^<]+)</loc>', body)
        self.assertEqual(len(locs), len(set(locs)), 'duplicate <loc> entries')

    @override_settings(SITE_URL='https://example.com')
    def test_no_double_slashes(self):
        body = self.client.get('/sitemap.xml').content.decode()
        self.assertNotIn('https://example.com//', body)

    @override_settings(SITE_URL='https://example.com')
    def test_custom_entries_are_normalised(self):
        """Admin-entered URLs get their slashes fixed and are de-duplicated."""
        from legal.models import Sitemap
        Sitemap.objects.create(url='about-us', priority=0.5, changefreq='monthly')
        Sitemap.objects.create(url='/about/', priority=0.5, changefreq='monthly')
        body = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('https://example.com/about-us/', body)
        self.assertEqual(body.count('https://example.com/about/</loc>'), 1)

    @override_settings(SITE_URL='https://example.com')
    def test_declares_image_namespace(self):
        body = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"', body)

    @override_settings(SITE_URL='https://example.com')
    def test_legal_pages_use_short_canonical_url(self):
        """The /legal/<slug>/ duplicate must not outrank the short URL."""
        from legal.models import LegalPage
        LegalPage.objects.create(page_type='privacy', slug='privacy-policy',
                                 title='Privacy Policy', content='<p>x</p>')
        body = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('https://example.com/privacy-policy/', body)
        self.assertNotIn('https://example.com/legal/privacy-policy/', body)

    @override_settings(SITE_URL='https://example.com')
    def test_image_loc_is_a_full_media_path(self):
        """Regression: <image:loc> used to render as just the bare origin."""
        import re
        from listings.models import Listing
        from realtors.models import Realtor

        realtor = Realtor.objects.create(
            name='Photo Agent', email='photo@example.com', phone='0711111111',
            is_verified=True,
        )
        Listing.objects.create(
            realtor=realtor, title='Photo House', address='2 Rd', city='Nairobi',
            state='Nairobi', zipcode='00100', price=200, bedrooms=2, bathrooms=1,
            photo_main='photos/2024/01/01/house.jpg', is_published=True,
        )
        body = self.client.get('/sitemap.xml').content.decode()
        locs = re.findall(r'<image:loc>([^<]+)</image:loc>', body)
        self.assertTrue(locs, 'expected at least one image entry')
        for loc in locs:
            with self.subTest(loc=loc):
                self.assertNotEqual(loc, 'https://example.com')
                self.assertIn('/media/', loc)
                self.assertTrue(loc.endswith(('.jpg', '.jpeg', '.png', '.webp', '.avif')))


class FaqPageTest(TestCase):
    """/faq/ must render, be linked, be indexed, and expose valid FAQ schema."""

    def setUp(self):
        self.response = self.client.get('/faq/')
        self.html = self.response.content.decode()

    def test_faq_page_returns_200(self):
        self.assertEqual(self.response.status_code, 200)

    def test_faq_url_name_resolves(self):
        self.assertEqual(reverse('faq'), '/faq/')

    def test_faq_has_exactly_one_of_each_head_tag(self):
        """Same regression that hit every other page: duplicate meta tags."""
        for pattern in [
            '<meta name="description"',
            '<meta name="keywords"',
            '<meta name="robots"',
            'rel="canonical"',
            'property="og:title"',
            'property="og:url"',
            '<title>',
        ]:
            with self.subTest(pattern=pattern):
                self.assertEqual(self.html.count(pattern), 1, pattern)

    def test_questions_and_answers_are_rendered(self):
        from pages.views import _faq_groups

        total = 0
        for group in _faq_groups():
            for item in group['items']:
                total += 1
                with self.subTest(question=item['q']):
                    self.assertIn(item['q'], self.html)
                    self.assertIn(item['a'][:40], self.html)
        self.assertEqual(self.html.count('<details class="faq-item" data-faq-item>'), total)

    @override_settings(SITE_URL='https://example.com')
    def test_canonical_points_at_faq(self):
        # Must re-fetch: setUp() runs before @override_settings takes effect.
        html = self.client.get('/faq/').content.decode()
        self.assertIn('rel="canonical" href="https://example.com/faq/"', html)

    def test_faq_schema_is_valid_json(self):
        """Regression: autoescaping turned the JSON into &quot; garbage."""
        import json
        import re

        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)
        self.assertTrue(blocks, 'expected structured data')
        for block in blocks:
            with self.subTest(block=block[:40]):
                self.assertNotIn('&quot;', block)
                json.loads(block)

    def test_faq_schema_matches_visible_questions(self):
        """Search engines penalise FAQ markup that is not on the page."""
        import json
        import re
        from pages.views import _faq_groups

        blocks = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)
        faq_blocks = [b for b in blocks
                      if json.loads(b).get('@type') == 'FAQPage']
        self.assertEqual(len(faq_blocks), 1, 'one FAQPage block expected')

        schema = json.loads(faq_blocks[0])
        visible = [item for group in _faq_groups() for item in group['items']]

        self.assertEqual(len(schema['mainEntity']), len(visible))
        self.assertEqual(
            [q['name'] for q in schema['mainEntity']],
            [item['q'] for item in visible])
        for q in schema['mainEntity']:
            with self.subTest(question=q['name']):
                self.assertEqual(q['@type'], 'Question')
                self.assertEqual(q['acceptedAnswer']['@type'], 'Answer')
                self.assertTrue(q['acceptedAnswer']['text'].strip())

    @override_settings(SITE_URL='https://example.com')
    def test_faq_is_in_sitemap(self):
        body = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('https://example.com/faq/', body)

    def test_faq_is_linked_from_navigation(self):
        home = self.client.get('/').content.decode()
        self.assertIn('href="/faq/"', home)


class UrlNameTest(TestCase):
    def test_url_names_resolve_without_duplicates(self):
        expected = {
            'index': '/',
            'about': '/about/',
            'faq': '/faq/',
            'contact': '/contacts/',
            'privacy_policy': '/privacy-policy/',
            'terms_of_service': '/terms-of-service/',
            'listings': '/listings/',
            'services': '/services/',
            'blog_list': '/blog/',
            'property_management': '/property-management/',
            'sitemap': '/sitemap.xml',
            'robots': '/robots.txt',
        }
        for name, path in expected.items():
            with self.subTest(name=name):
                self.assertEqual(reverse(name), path)
