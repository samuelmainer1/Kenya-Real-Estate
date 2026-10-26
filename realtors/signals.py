import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Realtor
from .utils import notify_admins_new_realtor

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Realtor)
def email_admins_on_new_realtor(sender, instance, created, **kwargs):
    if not created or instance.is_verified:
        return

    try:
        notify_admins_new_realtor(instance)
    except Exception:
        logger.exception('Failed to send new realtor notification for %s', instance.pk)
