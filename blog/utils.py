from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import BlogSubscription
from listings.models import ListingSubscription

def send_blog_notification(blog):
    """Send email notification to all active blog subscribers"""
    active_subscribers = BlogSubscription.objects.filter(is_active=True)
    
    for subscription in active_subscribers:
        try:
            subject = f"New Blog Post: {blog.title}"
            html_message = render_to_string('emails/blog_notification.html', {
                'blog': blog,
                'subscription': subscription,
            })
            
            send_mail(
                subject=subject,
                message=f"New blog post: {blog.title}\n\n{blog.short_description}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {subscription.email}: {e}")

def send_listing_notification(listing):
    """Send email notification to all active listing subscribers"""
    active_subscribers = ListingSubscription.objects.filter(is_active=True)
    
    for subscription in active_subscribers:
        try:
            subject = f"New Property Listed: {listing.title}"
            html_message = render_to_string('emails/listing_notification.html', {
                'listing': listing,
                'subscription': subscription,
            })
            
            send_mail(
                subject=subject,
                message=f"New property: {listing.title}\nPrice: ${listing.price:,}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscription.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {subscription.email}: {e}")