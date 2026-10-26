from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime


class RealtorQuerySet(models.QuerySet):
    def verified(self):
        return self.filter(is_verified=True)


class Realtor(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/')
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    is_mvp = models.BooleanField(default=False)
    hire_date = models.DateTimeField(default=datetime.now, blank=True)
    is_verified = models.BooleanField(
        default=False,
        help_text='Only admins can verify realtors. Verified realtors can have published listings.',
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='verified_realtors',
    )

    objects = RealtorQuerySet.as_manager()

    def __str__(self):
        return self.name

    def mark_verified(self, user):
        self.is_verified = True
        self.verified_at = timezone.now()
        self.verified_by = user
        self.save(update_fields=['is_verified', 'verified_at', 'verified_by'])

    def revoke_verification(self):
        self.is_verified = False
        self.verified_at = None
        self.verified_by = None
        self.save(update_fields=['is_verified', 'verified_at', 'verified_by'])
