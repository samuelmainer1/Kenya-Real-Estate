from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import MaintenanceSchedule, RentPayment, Tenant
from datetime import timedelta
from django.utils import timezone

@receiver(post_save, sender=MaintenanceSchedule)
def notify_maintenance_scheduled(sender, instance, created, **kwargs):
    """
    Send email notification when maintenance is scheduled
    """
    if created and instance.assigned_to:
        subject = f"New Maintenance Task: {instance.title}"
        context = {
            'maintenance': instance,
            'property': instance.managed_property.listing.title,
            'assigned_to': instance.assigned_to.get_full_name(),
        }
        
        html_message = render_to_string('property_management/emails/maintenance_scheduled.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.assigned_to.email],
            html_message=html_message,
            fail_silently=True,
        )

@receiver(pre_save, sender=MaintenanceSchedule)
def notify_maintenance_completed(sender, instance, **kwargs):
    """
    Send email notification when maintenance is completed
    """
    try:
        old_instance = MaintenanceSchedule.objects.get(pk=instance.pk)
        if old_instance.status != 'completed' and instance.status == 'completed':
            # Status changed to completed
            subject = f"Maintenance Completed: {instance.title}"
            context = {
                'maintenance': instance,
                'property': instance.managed_property.listing.title,
            }
            
            html_message = render_to_string('property_management/emails/maintenance_completed.html', context)
            plain_message = strip_tags(html_message)
            
            # Send to property manager (admin)
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                html_message=html_message,
                fail_silently=True,
            )
    except MaintenanceSchedule.DoesNotExist:
        pass

@receiver(post_save, sender=RentPayment)
def notify_rent_payment_received(sender, instance, created, **kwargs):
    """
    Send email notification when rent payment is received
    """
    if not created:
        try:
            old_instance = RentPayment.objects.get(pk=instance.pk)
            if old_instance.status != 'paid' and instance.status == 'paid':
                # Payment status changed to paid
                subject = f"Rent Payment Received - {instance.tenant.get_full_name()}"
                context = {
                    'payment': instance,
                    'tenant': instance.tenant,
                    'property': instance.tenant.managed_property.listing.title,
                }
                
                html_message = render_to_string('property_management/emails/rent_payment_received.html', context)
                plain_message = strip_tags(html_message)
                
                # Send to tenant
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [instance.tenant.email],
                    html_message=html_message,
                    fail_silently=True,
                )
        except RentPayment.DoesNotExist:
            pass

@receiver(post_save, sender=RentPayment)
def notify_overdue_rent(sender, instance, **kwargs):
    """
    Send email notification for overdue rent payments
    """
    if instance.status == 'overdue' and instance.is_overdue():
        # Check if we haven't sent a notification recently
        days_overdue = (timezone.now().date() - instance.due_date).days
        
        # Send notification on day 1, 7, 14, 30 of being overdue
        if days_overdue in [1, 7, 14, 30]:
            subject = f"Overdue Rent Payment Notice - {instance.tenant.get_full_name()}"
            context = {
                'payment': instance,
                'tenant': instance.tenant,
                'property': instance.tenant.managed_property.listing.title,
                'days_overdue': days_overdue,
            }
            
            html_message = render_to_string('property_management/emails/overdue_rent_notice.html', context)
            plain_message = strip_tags(html_message)
            
            # Send to tenant
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.tenant.email],
                html_message=html_message,
                fail_silently=True,
            )

@receiver(post_save, sender=Tenant)
def notify_tenant_added(sender, instance, created, **kwargs):
    """
    Send welcome email to new tenant
    """
    if created:
        subject = f"Welcome to {instance.managed_property.listing.title}"
        context = {
            'tenant': instance,
            'property': instance.managed_property.listing,
            'monthly_rent': instance.monthly_rent,
        }
        
        html_message = render_to_string('property_management/emails/tenant_welcome.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            html_message=html_message,
            fail_silently=True,
        )

