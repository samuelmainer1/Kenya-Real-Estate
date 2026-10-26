"""Tests for the client-facing account area.

The dashboard used to filter a single unfiltered booking list inside the
template loop, which rendered every booking in *both* the "viewings" and the
"stays" table. These tests pin the corrected behaviour.
"""

import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from listings.models import Booking, Listing
from realtors.models import Realtor


class DashboardTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            'owner', 'owner@example.com', 'pw-12345!', first_name='Amina',
        )
        cls.stranger = User.objects.create_user('stranger', 's@example.com', 'pw-12345!')
        cls.realtor = Realtor.objects.create(
            name='Test Realtor',
            photo='photos/x.jpg',
            phone='+254700000000',
            email='realtor@example.com',
            is_verified=True,
            hire_date=timezone.now(),
        )
        common = {
            'realtor': cls.realtor,
            'address': 'Test Road',
            'zipcode': '00100',
            'price': 100,
            'bedrooms': 3,
            'bathrooms': 2,
            'photo_main': 'photos/x.jpg',
        }
        cls.sale = Listing.objects.create(
            title='Karen Villa', property_type='sale',
            city='Nairobi', state='Nairobi', **common,
        )
        cls.airbnb = Listing.objects.create(
            title='Diani Beach House', property_type='airbnb',
            city='Diani', state='Kwale', **common,
        )

        today = datetime.date.today()
        cls.viewing = Booking.objects.create(
            listing=cls.sale,
            client=cls.owner,
            booking_type='viewing',
            date=today + datetime.timedelta(days=5),
            time=datetime.time(10, 0),
            client_email='owner@example.com',
        )
        cls.stay = Booking.objects.create(
            listing=cls.airbnb,
            client=cls.owner,
            booking_type='airbnb',
            check_in_date=today + datetime.timedelta(days=9),
            check_out_date=today + datetime.timedelta(days=12),
            client_email='owner@example.com',
        )


class DashboardSectionsTest(DashboardTestBase):
    def setUp(self):
        self.client.force_login(self.owner)
        self.response = self.client.get(reverse('dashboard'))
        self.html = self.response.content.decode()

    def _section(self, start_marker, end_marker):
        start = self.html.index(start_marker)
        end = self.html.index(end_marker)
        self.assertLess(start, end, f'{start_marker} must come before {end_marker}')
        return self.html[start:end]

    def test_dashboard_renders(self):
        self.assertEqual(self.response.status_code, 200)

    def test_viewing_section_excludes_stays(self):
        section = self._section('id="viewings"', 'id="stays"')
        self.assertIn('Karen Villa', section)
        self.assertNotIn('Diani Beach House', section)

    def test_stay_section_excludes_viewings(self):
        section = self._section('id="stays"', 'id="inquiries"')
        self.assertIn('Diani Beach House', section)
        self.assertNotIn('Karen Villa', section)

    def test_next_up_banner_shows_upcoming_booking(self):
        self.assertIn('cdash-next', self.html)
        self.assertIn('Your next viewing', self.html)

    def test_dashboard_is_noindex(self):
        self.assertIn('name="robots" content="noindex, nofollow"', self.html)


class CancelBookingTest(DashboardTestBase):
    def test_cancel_requires_login(self):
        response = self.client.post(
            reverse('cancel_booking', args=[self.viewing.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_other_users_cannot_cancel(self):
        self.client.force_login(self.stranger)
        response = self.client.post(reverse('cancel_booking', args=[self.viewing.pk]))
        self.assertEqual(response.status_code, 404)
        self.viewing.refresh_from_db()
        self.assertEqual(self.viewing.status, 'pending')

    def test_owner_can_cancel_pending_booking(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('cancel_booking', args=[self.viewing.pk]))
        self.assertEqual(response.status_code, 302)
        self.viewing.refresh_from_db()
        self.assertEqual(self.viewing.status, 'cancelled')

    def test_cancelled_booking_cannot_be_cancelled_again(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('cancel_booking', args=[self.viewing.pk]))
        # Force a status that is not cancellable, then try again.
        Booking.objects.filter(pk=self.viewing.pk).update(status='checked_out')
        response = self.client.post(
            reverse('cancel_booking', args=[self.viewing.pk]), follow=True)
        self.viewing.refresh_from_db()
        self.assertEqual(self.viewing.status, 'checked_out')
        self.assertContains(response, 'can no longer be cancelled')

    def test_cancel_page_rejects_get(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('cancel_booking', args=[self.viewing.pk]))
        self.assertEqual(response.status_code, 302)
        self.viewing.refresh_from_db()
        self.assertEqual(self.viewing.status, 'pending')


class ProfileTest(DashboardTestBase):
    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_profile_updates_name_and_email(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('profile'), {
            'first_name': 'Amina',
            'last_name': 'Wanjiku',
            'email': 'amina@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.last_name, 'Wanjiku')
        self.assertEqual(self.owner.email, 'amina@example.com')

    def test_profile_rejects_email_taken_by_another_user(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse('profile'), {
            'first_name': 'Amina',
            'last_name': 'Wanjiku',
            'email': 's@example.com',  # belongs to ``stranger``
        }, follow=True)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.email, 'owner@example.com')
        self.assertContains(response, 'already used by another account')

    def test_profile_keeps_own_email(self):
        """Saving your own email again must not trip the uniqueness check."""
        self.client.force_login(self.owner)
        response = self.client.post(reverse('profile'), {
            'first_name': 'Amina',
            'last_name': 'Wanjiku',
            'email': 'owner@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.email, 'owner@example.com')


