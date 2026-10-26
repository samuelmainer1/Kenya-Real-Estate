from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from listings.choices import price_choices, bedroom_choices, state_choices
from listings.models import Listing, ListingSubscription
from realtors.models import Realtor
from services.models import Service
from django.contrib import messages
from blog.models import BlogSubscription

def index(request):
    listings = Listing.objects.public().order_by('-list_date')[:3]
    featured_services = Service.objects.filter(is_featured=True, is_active=True).order_by('order')[:4]

    context = {
        'listings': listings,
        'featured_services': featured_services,
        'state_choices': state_choices,
        'bedroom_choices': bedroom_choices,
        'price_choices': price_choices
    }

    return render(request, 'pages/index.html', context)


def about(request):
    realtors = Realtor.objects.verified().order_by('-hire_date')
    mvp_realtors = Realtor.objects.verified().filter(is_mvp=True)

    context = {
        'realtors': realtors,
        'mvp_realtors': mvp_realtors
    }

    return render(request, 'pages/about.html', context)

def footer_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subscription_type = request.POST.get('type', 'both')  # both, blog, listing
        
        if email:
            blog_created = False
            listing_created = False
            blog_reactivated = False
            listing_reactivated = False
            
            if subscription_type in ['both', 'blog']:
                blog_subscription, blog_created = BlogSubscription.objects.get_or_create(
                    email=email,
                    defaults={'is_active': True}
                )
                if not blog_created and not blog_subscription.is_active:
                    blog_subscription.is_active = True
                    blog_subscription.save()
                    blog_reactivated = True
            
            if subscription_type in ['both', 'listing']:
                listing_subscription, listing_created = ListingSubscription.objects.get_or_create(
                    email=email,
                    defaults={'is_active': True}
                )
                if not listing_created and not listing_subscription.is_active:
                    listing_subscription.is_active = True
                    listing_subscription.save()
                    listing_reactivated = True
            
            # Provide appropriate feedback
            if blog_created or listing_created:
                messages.success(request, 'Successfully subscribed to updates!')
            elif blog_reactivated or listing_reactivated:
                messages.success(request, 'Welcome back! You are now subscribed again.')
            else:
                messages.info(request, 'You are already subscribed to our updates.')
        
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('index')


def _faq_groups():
    """Editorial FAQ content, grouped by topic.

    Kept in code (not the database) because it ships with the site, is the
    same for every visitor, and feeds the FAQPage structured data below - the
    visible answer and the JSON-LD answer must stay identical, so both are
    rendered from this single source.
    """
    return [
        {
            'slug': 'buying',
            'label': 'Buying Property',
            'icon': 'fas fa-home',
            'items': [
                {
                    'q': 'How do I start the process of buying a home in Kenya?',
                    'a': 'Start by browsing our verified listings and shortlisting the '
                         'properties that match your budget and preferred location. '
                         'Contact the assigned agent through the listing page or our '
                         'contact form, and we will arrange a viewing, walk you '
                         'through financing options, and guide you through the '
                         'documentation to completion.',
                },
                {
                    'q': 'Are all the properties on the site verified?',
                    'a': 'Listings are published by agents who have completed our '
                         'verification process, and listings from unverified agents '
                         'are not shown publicly. We still recommend that you or '
                         'your lawyer confirm title documents at the relevant land '
                         'registry before any money changes hands.',
                },
                {
                    'q': 'What costs should I budget for beyond the purchase price?',
                    'a': 'In Kenya, plan for stamp duty (4% for non-citizens and '
                         'companies, 2% for citizens), legal and conveyancing fees, '
                         'land search and registration fees, and any agent commission. '
                         'We give you a written cost breakdown before you commit so '
                         'there are no surprises.',
                },
                {
                    'q': 'Can I buy property in Kenya if I live abroad?',
                    'a': 'Yes. Non-residents can buy property, and we regularly work '
                         'with diaspora clients. Title can be held in your own name, '
                         'and you can appoint a lawyer or a trusted representative to '
                         'handle viewings and paperwork. Note that foreigners may only '
                         'hold leasehold title in Kenya, not freehold.',
                },
            ],
        },
        {
            'slug': 'renting',
            'label': 'Renting & Short Stays',
            'icon': 'fas fa-key',
            'items': [
                {
                    'q': 'What do I need to prepare to rent a house or apartment?',
                    'a': 'Have your ID or passport, proof of income such as payslips or '
                         'a contract, and usually the deposit plus one month of rent in '
                         'advance. For Airbnb and short stays you generally only need '
                         'identification and a booking confirmation.',
                },
                {
                    'q': 'How much deposit is normally required?',
                    'a': 'Long-term rentals in Kenya typically require one to two '
                         'months of rent as a security deposit, refundable at the end of '
                         'the tenancy subject to the condition of the property. Short '
                         'stays are paid in full at the time of booking.',
                },
                {
                    'q': 'Are the Airbnb listings managed by you?',
                    'a': 'Yes. Our managed short-stay units are furnished, cleaned between '
                         'guests, and supported by a local team you can reach during your '
                         'stay. Availability and nightly rates are shown on each listing.',
                },
            ],
        },
        {
            'slug': 'property-management',
            'label': 'Property Management',
            'icon': 'fas fa-building',
            'items': [
                {
                    'q': 'What is included in your property management service?',
                    'a': 'We handle tenant sourcing and vetting, rent collection and '
                         'remittance, routine maintenance coordination, inspections, '
                         'and financial reporting through the owner dashboard. You keep '
                         'visibility on occupancy, rent payments and maintenance from '
                         'anywhere.',
                },
                {
                    'q': 'What percentage do you charge to manage a property?',
                    'a': 'Our management fee is a percentage of the rent collected, agreed '
                         'per property because it depends on the unit type, the number of '
                         'units and the level of service required. Contact us for a '
                         'written quote for your property.',
                },
                {
                    'q': 'Do you manage properties outside Nairobi?',
                    'a': 'We manage properties in Nairobi and along the coast, including '
                         'Mombasa, Nyali and the surrounding areas. Reach out with your '
                         'location and we will confirm coverage and pricing.',
                },
            ],
        },
        {
            'slug': 'using-the-site',
            'label': 'Using the Website',
            'icon': 'fas fa-globe',
            'items': [
                {
                    'q': 'Do I need an account to browse properties?',
                    'a': 'No. Browsing, searching and viewing property details is open to '
                         'everyone. Creating a free account lets you save favourites, '
                         'track your inquiries and receive updates on new listings that '
                         'match your criteria.',
                },
                {
                    'q': 'How do I book a viewing or ask a question about a property?',
                    'a': 'Open the listing and use the contact form on the page, or email '
                         'and call the details shown in the footer. Include the property '
                         'name and your preferred dates and we will confirm a viewing '
                         'time within one business day.',
                },
                {
                    'q': 'Can I list my property with you?',
                    'a': 'Yes. Use the contact form to tell us about the property and your '
                         'goals, whether that is a sale, a long-term let or a short stay. '
                         'We will advise on pricing, prepare the listing and take the '
                         'photographs.',
                },
            ],
        },
        {
            'slug': 'payments-safety',
            'label': 'Payments & Safety',
            'icon': 'fas fa-shield-alt',
            'items': [
                {
                    'q': 'How do I know a payment request is genuine?',
                    'a': 'Only pay through the bank details, paybill or payment link that '
                         'appears on an official invoice from us. Treat any pressure to '
                         'send money urgently to a personal number as a red flag, and '
                         'when in doubt call our office using the number in the footer '
                         'to verify before paying.',
                },
                {
                    'q': 'Should I pay a deposit before viewing a property?',
                    'a': 'No. Never pay a booking or commitment fee before viewing the '
                         'property or, for diaspora clients, before your appointed '
                         'representative has viewed it and confirmed the title details. '
                         'A legitimate agency will never ask you to do so.',
                },
                {
                    'q': 'What should I check before signing a tenancy agreement?',
                    'a': 'Confirm the landlord or agency is authorised to let the '
                         'property, read the notice period and renewal terms, check what '
                         'utilities and service charges are included, and make sure the '
                         'deposit and refund conditions are written down. We can review '
                         'the agreement with you before you sign.',
                },
            ],
        },
    ]


def faq(request):
    """Frequently asked questions, with FAQPage structured data for search.

    The JSON-LD is built from the same data as the visible accordion so the
    two can never drift apart.
    """
    groups = _faq_groups()
    flat_items = [item for group in groups for item in group['items']]

    faq_schema = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {
                '@type': 'Question',
                'name': item['q'],
                'acceptedAnswer': {'@type': 'Answer', 'text': item['a']},
            }
            for item in flat_items
        ],
    }

    context = {
        'faq_groups': groups,
        'faq_count': len(flat_items),
        # JSON-LD is emitted verbatim: ensure_ascii keeps non-ASCII safe and
        # escaping the angle brackets stops "</script>" in any answer from
        # closing the tag early.
        'faq_schema_json': json.dumps(faq_schema, ensure_ascii=True)
                                 .replace('<', '\\u003C')
                                 .replace('>', '\\u003E'),
    }
    return render(request, 'pages/faq.html', context)


def contact(request):
    """Legacy /contact/ entry point.

    The live contact form lives in the contacts app (/contacts/ and
    /contacts/contact/). Redirect there so there is exactly one contact page
    (no duplicate content) while old links keep working.
    """
    return redirect('contact_page')

