from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from .models import Realtor


def get_admin_notification_emails():
    configured = getattr(settings, 'REALTOR_ADMIN_NOTIFY_EMAILS', None)
    if configured:
        return [email for email in configured if email]

    User = get_user_model()
    staff_emails = list(
        User.objects.filter(is_active=True, is_staff=True)
        .exclude(email='')
        .values_list('email', flat=True)
        .distinct()
    )
    if staff_emails:
        return staff_emails

    return [settings.DEFAULT_FROM_EMAIL]


def get_realtor_dashboard_context():
    pending_qs = Realtor.objects.filter(is_verified=False).order_by('-hire_date')
    return {
        'pending_realtors': pending_qs[:8],
        'pending_realtor_count': pending_qs.count(),
        'verified_realtor_count': Realtor.objects.filter(is_verified=True).count(),
        'total_realtor_count': Realtor.objects.count(),
    }


def notify_admins_new_realtor(realtor):
    admin_url = settings.SITE_URL.rstrip('/') + reverse(
        'admin:realtors_realtor_change',
        args=[realtor.pk],
    )
    pending_url = settings.SITE_URL.rstrip('/') + reverse(
        'admin:realtors_realtor_changelist',
    ) + '?is_verified__exact=0'

    context = {
        'realtor': realtor,
        'site_name': settings.SITE_NAME,
        'admin_url': admin_url,
        'pending_url': pending_url,
    }
    html_message = render_to_string('realtors/emails/new_realtor_pending.html', context)
    plain_message = strip_tags(html_message)
    subject = f'[{settings.SITE_NAME}] New realtor pending verification: {realtor.name}'

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        get_admin_notification_emails(),
        html_message=html_message,
        fail_silently=True,
    )
