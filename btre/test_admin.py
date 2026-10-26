"""Tests for the branded admin: index dashboard, user management, audit log."""

from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from listings.models import Listing, ListingSubscription
from realtors.models import Realtor
from django.utils import timezone


class AdminIndexDashboardTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('boss', 'boss@example.com', 'pw-12345!')
        realtor = Realtor.objects.create(
            name='Pending Realtor',
            photo='photos/x.jpg',
            phone='+254700000000',
            email='pending@example.com',
            is_verified=False,
            hire_date=timezone.now(),
        )
        Listing.objects.create(
            realtor=realtor,
            title='Hidden Listing',
            property_type='sale',
            address='Test Road',
            city='Nairobi',
            state='Nairobi',
            zipcode='00100',
            price=1000,
            bedrooms=2,
            bathrooms=1,
            photo_main='photos/x.jpg',
        )

    def test_dashboard_requires_staff(self):
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_dashboard_renders_for_staff(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_shows_kpis_and_attention_queue(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'Control Centre')
        self.assertContains(response, 'Needs your attention')
        self.assertContains(response, 'Realtors awaiting verification')
        self.assertContains(response, 'Published listings with unverified realtors')
        self.assertContains(response, 'Recent activity')

    def test_attention_links_are_prefiltered(self):
        """The queue must deep-link to the filtered changelist, not the bare one."""
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'is_verified__exact=0')

    def test_quick_actions_cover_every_editable_model(self):
        """Every model people manage must be reachable from the dashboard."""
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        for model in (Listing, ListingSubscription, Realtor, Group):
            url = reverse(
                f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist')
            self.assertContains(response, url)

    def test_dashboard_shows_app_list_for_fallback(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'Browse all registered models')


class AdminRegistrationTest(TestCase):
    def test_user_and_group_are_registered(self):
        self.assertTrue(admin.site.is_registered(User))
        self.assertTrue(admin.site.is_registered(Group))

    def test_subscriptions_are_registered(self):
        self.assertTrue(admin.site.is_registered(ListingSubscription))

    def test_user_admin_lists_roles(self):
        model_admin = admin.site._registry[User]
        self.assertIn('role', model_admin.list_display)
        self.assertIn('full_name', model_admin.list_display)

    def test_user_changelist_renders(self):
        admin_user = User.objects.create_superuser('boss', 'boss@example.com', 'pw-12345!')
        self.client.force_login(admin_user)
        response = self.client.get(reverse('admin:auth_user_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Superuser')

    def test_user_add_page_renders(self):
        admin_user = User.objects.create_superuser('boss', 'boss@example.com', 'pw-12345!')
        self.client.force_login(admin_user)
        response = self.client.get(reverse('admin:auth_user_add'))
        self.assertEqual(response.status_code, 200)

    def test_audit_log_is_read_only(self):
        model_admin = admin.site._registry[admin.models.LogEntry]

        class _Req:
            pass

        self.assertFalse(model_admin.has_add_permission(_Req()))
        self.assertFalse(model_admin.has_change_permission(_Req()))
        self.assertFalse(model_admin.has_delete_permission(_Req()))


class AdminLoginPageTest(TestCase):
    """The login screen is the first thing an owner sees; it must be branded."""

    def test_login_renders_branded_split_layout(self):
        response = self.client.get(reverse('admin:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/login.html')
        self.assertContains(response, 'kc-login')
        # Real property photography rather than a plain form on white.
        self.assertContains(response, 'img/real2.avif')
        # The public site's stylesheet comes with it.
        self.assertContains(response, 'css/admin-login.css')

    def test_login_shows_brand_not_hostname(self):
        """`site_name` is the host in Django templates - branding must not use it."""
        response = self.client.get(reverse('admin:login'))
        self.assertContains(response, 'Kenya Realestate Platform')
        self.assertNotContains(response, '<strong>testserver</strong>')

    def test_login_still_authenticates(self):
        User.objects.create_superuser('boss', 'boss@example.com', 'pw-12345!')
        response = self.client.post(
            reverse('admin:login'),
            {'username': 'boss', 'password': 'pw-12345!', 'next': '/admin/'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith('/admin/'))

    def test_login_shows_error_on_bad_credentials(self):
        response = self.client.post(
            reverse('admin:login'),
            {'username': 'nobody', 'password': 'wrong'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'kc-login-error')


class AdminSidebarTest(TestCase):
    """The grouped Control Centre navigation replaces Django's flat app list."""

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('boss', 'boss@example.com', 'pw-12345!')

    def test_sidebar_renders_on_the_dashboard(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'id="kc-sidebar"')
        self.assertContains(response, 'Filter menu')
        for section in ('Overview', 'Listings &amp; bookings', 'Clients &amp; leads',
                        'Property management', 'Content &amp; blog', 'Site settings',
                        'Users &amp; access', 'Site shortcuts'):
            self.assertContains(response, section)

    def test_sidebar_renders_on_changelists(self):
        """Every admin page gets the nav, not just the dashboard."""
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:listings_listing_changelist'))
        self.assertContains(response, 'id="kc-sidebar"')

    def test_current_page_is_marked(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:listings_listing_changelist'))
        self.assertContains(response, 'kc-nav-link-current')

    def test_sidebar_lists_every_model_from_the_config(self):
        client = self.client
        client.force_login(self.staff)
        response = client.get(reverse('admin:index'))
        for model in (Listing, ListingSubscription, Realtor, Group, User):
            url = reverse(f'admin:{model._meta.app_label}_{model._meta.model_name}_changelist')
            self.assertContains(response, url)

    def test_settings_model_is_reachable(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, reverse('admin:core_globalsettings_changelist'))

    def test_sidebar_hides_models_without_permission(self):
        """A staff user with no model permissions sees no model links."""
        limited = User.objects.create_user('limited', 'l@example.com', 'pw-12345!', is_staff=True)
        self.client.force_login(limited)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse('admin:listings_listing_changelist'))

    def test_site_shortcuts_link_to_public_pages(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin:index'))
        for name in ('index', 'listings', 'blog_list', 'contact_page', 'privacy_policy'):
            self.assertContains(response, reverse(name))
