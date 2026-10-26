from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Contact

VALID = {
    'name': 'Test User',
    'email': 'test@example.com',
    'phone': '+254700000000',
    'message': 'Interested in a villa.',
    'inquiry_type': 'buying',
}


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ContactFormTests(TestCase):
    def setUp(self):
        self.url = reverse('contact')

    def test_get_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts/contact.html')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_legacy_contact_page_redirects(self):
        """Old /contacts/contact/ links must 301 to the canonical page."""
        response = self.client.get('/contacts/contact/')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], '/contacts/')

    def test_root_contact_redirects(self):
        response = self.client.get('/contact/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.redirect_chain[-1][0], '/contacts/')

    def test_valid_submission_saves_and_sends_email(self):
        response = self.client.post(self.url, VALID)

        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        self.assertEqual(Contact.objects.count(), 1)

        contact = Contact.objects.get()
        self.assertEqual(contact.name, 'Test User')
        self.assertEqual(contact.email, 'test@example.com')
        self.assertIsNotNone(contact.contact_date)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Test User', mail.outbox[0].body)

    def test_contact_date_default_is_timezone_aware(self):
        """datetime.now would emit a naive-datetime RuntimeWarning."""
        contact = Contact.objects.create(
            name='A', email='a@b.com', phone='1', listing='', listing_id=0)
        self.assertIsNotNone(contact.contact_date.tzinfo)

    def test_missing_fields_do_not_save(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertContains(response, 'Please enter your name.')
        self.assertContains(response, 'Please enter your email address.')
        self.assertContains(response, 'Please enter your phone number.')
        self.assertContains(response, 'Please tell us how we can help.')

    def test_invalid_email_does_not_save(self):
        response = self.client.post(self.url, dict(VALID, email='not-an-email'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertContains(response, 'Please enter a valid email address.')

    def test_entered_values_are_preserved_on_error(self):
        response = self.client.post(self.url, dict(VALID, phone=''))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test User')
        self.assertContains(response, 'test@example.com')
        self.assertContains(response, 'Interested in a villa.')

    def test_honeypot_blocks_spam(self):
        response = self.client.post(self.url, dict(VALID, website='http://spam.example'))

        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_overlong_input_is_truncated(self):
        self.client.post(self.url, dict(VALID, name='X' * 500, message='Y' * 9000))

        contact = Contact.objects.get()
        self.assertEqual(len(contact.name), 200)
        self.assertEqual(len(contact.message), 5000)

    def test_email_failure_is_logged_and_saves_inquiry(self):
        """A dead SMTP server must not lose the inquiry nor lie in the log."""
        with patch('contacts.views.send_mail', side_effect=OSError('SMTP down')):
            with self.assertLogs('contacts.views', level='ERROR') as logs:
                response = self.client.post(self.url, VALID)

        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertTrue(any('EMAIL DELIVERY FAILED' in line for line in logs.output))

    def test_csrf_is_enforced(self):
        client = self.client_class(enforce_csrf_checks=True)
        response = client.post(self.url, VALID)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Contact.objects.count(), 0)

