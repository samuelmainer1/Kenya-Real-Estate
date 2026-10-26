"""Site-wide settings that used to be hard-coded in ``btre/settings.py``.

``SITE_NAME``, ``SITE_TAGLINE`` and the contact/social details were only
editable by editing Python and redeploying. Every one of them is shown on the
public site, so they belong in the Control Centre like everything else.

The model is intentionally a **singleton**: :meth:`GlobalSettings.load` always
returns the same row (creating it on first use) and the admin blocks adding a
second one. Fields fall back to the ``settings.py`` defaults when left blank, so
existing behaviour is unchanged until an admin actually fills something in.
"""

from django.conf import settings
from django.db import models


class GlobalSettings(models.Model):
    """One editable row describing the business behind the website."""

    site_name = models.CharField(
        max_length=120,
        blank=True,
        help_text='Shown in the navbar, page titles and emails.',
    )
    site_tagline = models.CharField(
        max_length=160,
        blank=True,
        help_text='Short line under the site name, e.g. "Premium Real Estate in Kenya".',
    )
    phone = models.CharField(max_length=40, blank=True, help_text='Main public phone number.')
    whatsapp_number = models.CharField(
        max_length=40,
        blank=True,
        help_text='Digits only, including country code, e.g. 254712345678.',
    )
    email = models.EmailField(blank=True, help_text='Main public contact email.')
    physical_address = models.CharField(max_length=200, blank=True)
    office_hours = models.CharField(
        max_length=120,
        blank=True,
        help_text='e.g. "Mon – Fri, 8:00am – 6:00pm".',
    )
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    # Announcement bar: the one place to broadcast something site-wide without
    # a developer touching templates.
    announcement = models.CharField(
        max_length=220,
        blank=True,
        help_text='Optional banner text shown across the public site. Leave blank to hide.',
    )
    announcement_active = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Global settings'
        verbose_name_plural = 'Global settings'

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        # Enforce the singleton at the model layer, not just in the admin, so a
        # shell session cannot create a second row. ``pk=1`` also keeps the row
        # in place when it was created by hand with a different id.
        self.pk = 1
        super().save(*args, **kwargs)

    # ---------- values with settings.py fallbacks ----------

    @property
    def display_name(self):
        return self.site_name or getattr(settings, 'SITE_NAME', 'Kenya Realestate Platform')

    @property
    def display_tagline(self):
        return self.site_tagline or getattr(settings, 'SITE_TAGLINE', '')

    @classmethod
    def load(cls):
        """Return the singleton row, creating it on first use.

        Deliberately uncached: it is a single primary-key lookup rendered once
        per public page, and caching it per-process meant an edit made in one
        worker was invisible to the others until they restarted.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
