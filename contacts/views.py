from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Contact
from realtors.models import Realtor
import logging

logger = logging.getLogger(__name__)

INQUIRY_TYPES = [
    ("buying", "Buying a property"),
    ("renting", "Renting a property"),
    ("selling", "Selling or listing my property"),
    ("management", "Property management"),
    ("airbnb", "Airbnb management"),
    ("valuation", "Property valuation"),
    ("other", "Something else"),
]

# Field limits - keep in sync with contacts.models.Contact
MAX_NAME_LENGTH = 200
MAX_EMAIL_LENGTH = 100
MAX_PHONE_LENGTH = 100
MAX_MESSAGE_LENGTH = 5000


def _clean_post(request):
    """Pull and truncate the submitted contact fields.

    Returns (data, errors). ``errors`` is a list of user-facing messages.
    """
    data = {
        'listing': (request.POST.get('listing') or '').strip()[:200],
        'listing_id': (request.POST.get('listing_id') or '').strip(),
        'name': (request.POST.get('name') or '').strip()[:MAX_NAME_LENGTH],
        'email': (request.POST.get('email') or '').strip()[:MAX_EMAIL_LENGTH],
        'phone': (request.POST.get('phone') or '').strip()[:MAX_PHONE_LENGTH],
        'message': (request.POST.get('message') or '').strip()[:MAX_MESSAGE_LENGTH],
        'realtor_email': (request.POST.get('realtor_email') or '').strip(),
        'inquiry_type': (request.POST.get('inquiry_type') or '').strip(),
    }

    errors = []
    if not data['name']:
        errors.append('Please enter your name.')
    if not data['email']:
        errors.append('Please enter your email address.')
    else:
        try:
            validate_email(data['email'])
        except ValidationError:
            errors.append('Please enter a valid email address.')
    if not data['phone']:
        errors.append('Please enter your phone number.')
    if not data['message']:
        errors.append('Please tell us how we can help.')
    if data['realtor_email']:
        try:
            validate_email(data['realtor_email'])
        except ValidationError:
            data['realtor_email'] = ''

    return data, errors



def contact(request):
    # Context for the revamped contact page (team you can reach, saved on GET and after POST)
    context = {
        'realtors': Realtor.objects.verified().order_by('-is_mvp', 'hire_date'),
        'inquiry_types': INQUIRY_TYPES,
        'default_name': request.user.get_full_name() if request.user.is_authenticated else '',
        'default_email': request.user.email if request.user.is_authenticated else '',
    }

    if request.method == 'POST':
        # Honeypot: bots fill hidden fields; humans never see them
        website = request.POST.get('website', '').strip()
        if website:
            logger.info(f"Blocked honeypot spam submission pretending to be {request.POST.get('name', '')}")
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('contact')

        data, errors = _clean_post(request)
        name = data['name']
        email = data['email']
        phone = data['phone']
        message = data['message']
        listing = data['listing']
        realtor_email = data['realtor_email']
        type_label = dict(INQUIRY_TYPES).get(data['inquiry_type'], '')

        # Convert listing_id to int if possible, else set to 0
        try:
            listing_id_int = int(data['listing_id']) if data['listing_id'] else 0
        except ValueError:
            listing_id_int = 0

        if errors:
            for error in errors:
                messages.error(request, error)
            # Re-render the page with what the visitor typed so nothing is lost.
            context['form_data'] = data
            return render(request, 'contacts/contact.html', context)

        # Check if user has made inquiry already (only for property inquiries)
        if listing_id_int and request.user.is_authenticated:
            has_contacted = Contact.objects.all().filter(listing_id=listing_id_int, user=request.user)
            if has_contacted:
                messages.error(request, 'You have already made an inquiry for this listing')
                return redirect('listing_legacy', listing_id=listing_id_int)

        # Save contact to database first
        contact = Contact(
            listing=listing,
            listing_id=listing_id_int,
            name=name,
            email=email,
            phone=phone,
            message=message,
            user=request.user if request.user.is_authenticated else None
        )
        contact.save()

        # Notify the team. The inquiry is already saved, so an email failure must
        # not break the visitor's experience - but it MUST be logged loudly.
        notify_to = realtor_email or settings.CONTACT_NOTIFY_EMAIL
        subject = 'Property Listing Inquiry' if listing_id_int else 'New Contact Inquiry'
        if type_label:
            subject += f' ({type_label})'
        email_message = (
            f'There has been an inquiry for {listing or "General Contact"}.'
            f'\n\nMessage: {message}\nFrom: {name} ({email}, {phone})'
        )
        try:
            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                [notify_to],
                fail_silently=False,
            )
            logger.info("Contact inquiry #%s emailed to %s", contact.pk, notify_to)
        except (BadHeaderError, Exception) as exc:  # noqa: B014 - SMTP raises many types
            logger.error(
                "EMAIL DELIVERY FAILED for contact inquiry #%s (to %s): %s: %s",
                contact.pk, notify_to, type(exc).__name__, exc,
            )
            messages.warning(
                request,
                'Your message was saved, but our email notification could not be '
                'sent. Please call us if you need an urgent response.',
            )

        # Success message
        if listing_id_int:
            messages.success(request, 'Your request has been submitted, a realtor will get back to you soon')
            return redirect('listing_legacy', listing_id=listing_id_int)

        messages.success(request, 'Thank you for contacting us! We have received your message and will get back to you soon.')
        return redirect('contact')

    # For GET requests, render the contact page
    return render(request, 'contacts/contact.html', context)


