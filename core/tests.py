"""Tests for site-wide settings edited in the Control Centre.

``GlobalSettings`` is the singleton that used to be hard-coded in
``btre/settings.py``. It must (a) always be the same row, (b) fall back to the
settings.py defaults, and (c) actually change what the public site renders.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.models import GlobalSettings


class GlobalSettingsModelTest(TestCase):
    def test_load_creates_one_row(self):
        first = GlobalSettings.load()
        second = GlobalSettings.load()
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(first.pk, 1)
        self.assertEqual(GlobalSettings.objects.count(), 1)

    def test_save_forces_the_singleton_pk(self):
        settings_obj = GlobalSettings(site_name='Renamed')
        settings_obj.save()
        self.assertEqual(settings_obj.pk, 1)
        self.assertEqual(GlobalSettings.objects.count(), 1)

    def test_blank_fields_fall_back_to_settings_py(self):
        # settings.py ships SITE_NAME='Kenya Realestate Platform'.
        self.assertEqual(GlobalSettings.load().display_name, 'Kenya Realestate Platform')

    def test_saved_name_overrides_fallback(self):
        obj = GlobalSettings.load()
        obj.site_name = 'Acme Homes'
        obj.save()
        self.assertEqual(GlobalSettings.load().display_name, 'Acme Homes')

    def test_edits_are_visible_to_a_fresh_read(self):
        """No caching layer: an edit in one process must be seen by the next."""
        GlobalSettings.load()
        GlobalSettings.objects.filter(pk=1).update(site_name='Fresh Name')
        self.assertEqual(GlobalSettings.load().display_name, 'Fresh Name')


class GlobalSettingsAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser('boss', 'boss@example.com', 'pw-12345!')

    def test_changelist_opens_the_single_form(self):
        self.client.force_login(self.staff)
        obj = GlobalSettings.load()
        response = self.client.get(reverse('admin:core_globalsettings_changelist'))
        self.assertRedirects(
            response,
            reverse('admin:core_globalsettings_change', args=[obj.pk]),
            fetch_redirect_response=False,
        )

    def test_change_form_renders(self):
        self.client.force_login(self.staff)
        obj = GlobalSettings.load()
        response = self.client.get(reverse('admin:core_globalsettings_change', args=[obj.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Site-wide announcement')
        self.assertContains(response, 'whatsapp_number')

    def test_no_second_row_can_be_added(self):
        self.client.force_login(self.staff)
        GlobalSettings.load()
        response = self.client.get(reverse('admin:core_globalsettings_add'))
        self.assertEqual(response.status_code, 403)

    def test_row_cannot_be_deleted(self):
        from django.contrib import admin

        from core.admin import GlobalSettingsAdmin

        registered = admin.site._registry[GlobalSettings]
        self.assertIsInstance(registered, GlobalSettingsAdmin)
        self.assertFalse(registered.has_delete_permission(request=None))


class GlobalSettingsPublicSiteTest(TestCase):
    """Editing settings must visibly change the public site."""

    def test_site_name_appears_on_homepage(self):
        obj = GlobalSettings.load()
        obj.site_name = 'Acme Homes Kenya'
        obj.save()
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Acme Homes Kenya')

    def test_announcement_only_shows_when_active(self):
        obj = GlobalSettings.load()
        obj.announcement = 'New Ruiru listings are live'
        obj.announcement_active = False
        obj.save()
        self.assertNotContains(self.client.get(reverse('index')), 'New Ruiru listings are live')

        obj.announcement_active = True
        obj.save()
        self.assertContains(self.client.get(reverse('index')), 'New Ruiru listings are live')

    def test_topbar_contact_details_come_from_settings(self):
        obj = GlobalSettings.load()
        obj.phone = '+254 700 111 222'
        obj.email = 'hello@example.com'
        obj.save()
        response = self.client.get(reverse('index'))
        self.assertContains(response, '+254 700 111 222')
        self.assertContains(response, 'hello@example.com')
        # tel: links must not contain the spaces used for display.
        self.assertContains(response, 'tel:+254700111222')

    def test_social_links_are_omitted_when_unset(self):
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'class="topbar-social-link" aria-label="Pinterest"')

