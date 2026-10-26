"""Admin index (``/admin/``) dashboard.

Everything on the site is editable in the admin, but Django's default index is
just an alphabetical list of app labels. That makes it hard to answer the
questions a site owner actually asks: *what needs my attention right now?*

This module replaces ``admin.site.index`` with a view that adds:

* headline KPIs (listings, inquiries, bookings, portfolio value, rent),
* a "needs attention" queue with deep links pre-filtered to the items that
  are waiting on an admin decision,
* a complete quick-action panel covering every model in the project,
* a recent-activity feed.

All queries go through ``_safe``: the dashboard is the busiest page in the
admin, so one missing table or unapplied migration must not take the whole
page down.
"""

from datetime import timedelta

from django.contrib import admin
from django.db.models import Sum
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from realtors.utils import get_realtor_dashboard_context


def _safe(fn, default=None):
    """Run ``fn`` and swallow database errors.

    The dashboard must render even when a feature app has not been migrated
    yet (for example on a brand-new deployment), so callers never have to
    guard each individual query.
    """
    try:
        return fn()
    except Exception:  # noqa: BLE001 - the dashboard must never 500
        return default


def _reverse(name, *args):
    """Reverse an admin URL, returning ``None`` when the model is absent.

    Keeps the template free of ``{% url %}`` calls that would raise
    ``NoReverseMatch`` for models removed in a future refactor.
    """
    try:
        return reverse(name, args=args or None)
    except NoReverseMatch:
        return None


def _count(model, **filters):
    if model is None:
        return 0
    return _safe(lambda: model.objects.filter(**filters).count(), 0)


# Public (non-staff) helpers --------------------------------------------------
#
# The dashboard is reachable by any staff member, not just superusers. Links to
# changelists they cannot open would bounce them to "permission denied", so the
# panels below ask these helpers before rendering a destination.


def _can(user, perm):
    """Whether ``user`` holds ``perm`` (``'app.action_model'``)."""
    if user is None:
        return True
    return bool(_safe(lambda: user.has_perm(perm), False))


def _permitted_url(user, changelist_name, perm):
    """Changelist URL, or ``None`` when the user may not open it."""
    return _reverse(changelist_name) if _can(user, perm) else None


def _kpis(last_week, user=None):
    """Headline numbers shown as cards at the top of the dashboard.

    A card is only a link when the viewer can open the underlying changelist;
    otherwise it renders as a plain (non-clickable) figure.
    """
    from blog.models import Blog
    from contacts.models import Contact
    from listings.models import Booking, Listing
    from property_management.models import ManagedProperty, RentPayment
    from realtors.models import Realtor

    listings = _count(Listing)
    published = _count(Listing, is_published=True)
    portfolio_value = _safe(
        lambda: Listing.objects.filter(is_published=True).aggregate(
            total=Sum('price'))['total'] or 0,
        0,
    )
    rent_collected = _safe(
        lambda: RentPayment.objects.aggregate(total=Sum('amount_paid'))['total'] or 0,
        0,
    )

    return [
        {
            'label': 'Listings',
            'value': listings,
            'meta': f'{published} published · {listings - published} draft',
            'icon': 'listings',
            'url': _permitted_url(user, 'admin:listings_listing_changelist', 'listings.view_listing'),
            'tone': 'blue',
        },
        {
            'label': 'New inquiries',
            'value': _count(Contact, contact_date__gte=last_week),
            'meta': f'{_count(Contact)} all time',
            'icon': 'inquiries',
            'url': _permitted_url(user, 'admin:contacts_contact_changelist', 'contacts.view_contact'),
            'tone': 'amber',
        },
        {
            'label': 'Bookings',
            'value': _count(Booking),
            'meta': f'{_count(Booking, status="pending")} awaiting confirmation',
            'icon': 'bookings',
            'url': _permitted_url(user, 'admin:listings_booking_changelist', 'listings.view_booking'),
            'tone': 'violet',
        },
        {
            'label': 'Realtors',
            'value': _count(Realtor),
            'meta': f'{_count(Realtor, is_verified=True)} verified',
            'icon': 'realtors',
            'url': _permitted_url(user, 'admin:realtors_realtor_changelist', 'realtors.view_realtor'),
            'tone': 'emerald',
        },
        {
            'label': 'Portfolio value',
            'value': portfolio_value,
            'meta': 'Across published listings',
            'icon': 'value',
            'url': _permitted_url(user, 'admin:listings_listing_changelist', 'listings.view_listing'),
            'is_currency': True,
            'tone': 'navy',
        },
        {
            'label': 'Rent collected',
            'value': rent_collected,
            'meta': f'{_count(ManagedProperty)} managed properties',
            'icon': 'revenue',
            'url': _permitted_url(
                user, 'admin:property_management_rentpayment_changelist',
                'property_management.view_rentpayment',
            ),
            'is_currency': True,
            'tone': 'teal',
        },
        {
            'label': 'Blog posts',
            'value': _count(Blog),
            'meta': f'{_count(Blog, published=True)} published',
            'icon': 'content',
            'url': _permitted_url(user, 'admin:blog_blog_changelist', 'blog.view_blog'),
            'tone': 'slate',
        },
    ]


def _filter_url(changelist_name, query):
    """Build a changelist URL with a pre-applied filter, or ``None``."""
    base = _reverse(changelist_name)
    return f'{base}?{query}' if base else None


def _attention_queue(user=None):
    """Everything waiting on an admin decision, in priority order.

    Each block is gated on the permission that would let the viewer act on it,
    so a content editor never sees a "review realtors" prompt they cannot fulfil.
    """
    from blog.models import Blog, BlogComment
    from contacts.models import Contact
    from listings.models import Booking, Listing
    from realtors.models import Realtor
    from testimonials.models import Testimonial

    items = []

    pending_realtors_count = _count(Realtor, is_verified=False)
    if pending_realtors_count and _can(user, 'realtors.change_realtor'):
        pending_realtors = _safe(
            lambda: Realtor.objects.filter(is_verified=False).order_by('-hire_date')[:5],
            [],
        )
        items.append({
            'key': 'realtors',
            'title': 'Realtors awaiting verification',
            'description': 'Unverified realtors cannot publish listings.',
            'count': pending_realtors_count,
            'items': [
                {
                    'label': r.name,
                    'detail': f'{r.email} · {r.phone}',
                    'url': _reverse('admin:realtors_realtor_change', r.pk),
                }
                for r in pending_realtors
            ],
            'action_label': 'Review realtors',
            'action_url': _filter_url('admin:realtors_realtor_changelist', 'is_verified__exact=0'),
        })

    blocked = _count(Listing, is_published=True, realtor__is_verified=False)
    if blocked and _can(user, 'listings.change_listing'):
        items.append({
            'key': 'blocked-listings',
            'title': 'Published listings with unverified realtors',
            'description': 'These stay hidden from the public site until a realtor is verified.',
            'count': blocked,
            'items': [],
            'action_label': 'Fix listings',
            'action_url': _filter_url(
                'admin:listings_listing_changelist',
                'is_published__exact=1&realtor__is_verified__exact=0',
            ),
        })

    pending_bookings_count = _count(Booking, status='pending')
    if pending_bookings_count and _can(user, 'listings.change_booking'):
        pending_bookings = _safe(
            lambda: Booking.objects.filter(status='pending').select_related('listing')[:5],
            [],
        )
        items.append({
            'key': 'bookings',
            'title': 'Bookings awaiting confirmation',
            'description': 'Clients are waiting to hear back.',
            'count': pending_bookings_count,
            'items': [
                {
                    'label': b.listing.title if b.listing_id else 'Listing removed',
                    'detail': b.get_booking_type_display_custom(),
                    'url': _reverse('admin:listings_booking_change', b.pk),
                }
                for b in pending_bookings
            ],
            'action_label': 'Manage bookings',
            'action_url': _filter_url('admin:listings_booking_changelist', 'status__exact=pending'),
        })

    pending_testimonials_count = _count(Testimonial, status='pending')
    if pending_testimonials_count and _can(user, 'testimonials.change_testimonial'):
        pending_testimonials = _safe(
            lambda: Testimonial.objects.filter(status='pending').select_related('listing')[:5],
            [],
        )
        items.append({
            'key': 'testimonials',
            'title': 'Testimonials awaiting moderation',
            'description': 'Approve them to show on the site and homepage.',
            'count': pending_testimonials_count,
            'items': [
                {
                    'label': t.name,
                    'detail': f'{t.rating}★ · {t.title}',
                    'url': _reverse('admin:testimonials_testimonial_change', t.pk),
                }
                for t in pending_testimonials
            ],
            'action_label': 'Moderate testimonials',
            'action_url': _filter_url(
                'admin:testimonials_testimonial_changelist', 'status__exact=pending'),
        })

    drafts_count = _count(Blog, published=False)
    if drafts_count and _can(user, 'blog.change_blog'):
        drafts = _safe(
            lambda: Blog.objects.filter(published=False).order_by('-posted_at')[:5],
            [],
        )
        items.append({
            'key': 'blog',
            'title': 'Unpublished blog posts',
            'description': 'Drafts and scheduled posts that are not live yet.',
            'count': drafts_count,
            'items': [
                {
                    'label': b.title,
                    'detail': (
                        timezone.localtime(b.scheduled_at).strftime('Scheduled %d %b %Y')
                        if b.scheduled_at else 'Draft'
                    ),
                    'url': _reverse('admin:blog_blog_change', b.pk),
                }
                for b in drafts
            ],
            'action_label': 'Open blog',
            'action_url': _filter_url('admin:blog_blog_changelist', 'published__exact=0'),
        })

    # Maintenance scheduled for today or already overdue.
    from property_management.models import MaintenanceSchedule

    maintenance_due = _count(
        MaintenanceSchedule,
        status__in=['scheduled', 'in_progress'],
        scheduled_date__lte=timezone.localdate(),
    )
    if maintenance_due and _can(user, 'property_management.view_maintenanceschedule'):
        items.append({
            'key': 'maintenance',
            'title': 'Maintenance due or overdue',
            'description': 'Scheduled tasks that need attention today.',
            'count': maintenance_due,
            'items': [],
            'action_label': 'Open maintenance',
            'action_url': _reverse('admin:property_management_maintenanceschedule_changelist'),
        })

    recent_inquiries = _count(Contact, contact_date__gte=timezone.now() - timedelta(days=7))
    if recent_inquiries and _can(user, 'contacts.view_contact'):
        items.append({
            'key': 'inquiries',
            'title': 'Inquiries from the last 7 days',
            'description': 'Follow up while the lead is still warm.',
            'count': recent_inquiries,
            'items': [],
            'action_label': 'Open inquiries',
            'action_url': _reverse('admin:contacts_contact_changelist'),
        })

    comment_count = _count(BlogComment)
    if comment_count and _can(user, 'blog.view_blogcomment'):
        recent_comments = _safe(
            lambda: BlogComment.objects.select_related('blog', 'user').order_by('-created_at')[:5],
            [],
        )
        items.append({
            'key': 'comments',
            'title': 'Blog comments',
            'description': 'Moderate the conversation on your articles.',
            'count': comment_count,
            'items': [
                {
                    'label': c.user.username if c.user_id else 'Anonymous',
                    'detail': (c.content or '')[:60],
                    'url': _reverse('admin:blog_blogcomment_change', c.pk),
                }
                for c in recent_comments
            ],
            'action_label': 'Open comments',
            'action_url': _reverse('admin:blog_blogcomment_changelist'),
        })

    return items


def _quick_actions(user=None):
    """Every model in the project, grouped so nothing is out of reach.

    Links the viewer may not open are omitted, so this panel mirrors their real
    permissions rather than advertising a wall of "permission denied" pages.
    """

    def link(changelist_name, add_name, label, perm):
        if not _can(user, perm):
            return None
        changelist = _reverse(changelist_name)
        if not changelist:
            return None
        return {
            'label': label,
            'changelist': changelist,
            'add': _reverse(add_name),
        }

    def report(url_name, label, perm):
        """A link to a staff report view rather than a model changelist.

        Reports have no "add" form, so ``add`` is always ``None`` and the
        template simply omits the ``+`` button.
        """
        if not _can(user, perm):
            return None
        url = _reverse(url_name)
        if not url:
            return None
        return {'label': label, 'changelist': url, 'add': None}

    groups = [
        {
            'title': 'Listings & bookings',
            'icon': 'listings',
            'links': [
                link('admin:listings_listing_changelist', 'admin:listings_listing_add', 'Listings', 'listings.view_listing'),
                link('admin:listings_booking_changelist', 'admin:listings_booking_add', 'Bookings', 'listings.view_booking'),
                link('admin:listings_listingsubscription_changelist', 'admin:listings_listingsubscription_add', 'Listing alerts', 'listings.view_listingsubscription'),
                link('admin:realtors_realtor_changelist', 'admin:realtors_realtor_add', 'Realtors', 'realtors.view_realtor'),
            ],
        },
        {
            'title': 'Leads & clients',
            'icon': 'inquiries',
            'links': [
                link('admin:contacts_contact_changelist', 'admin:contacts_contact_add', 'Inquiries', 'contacts.view_contact'),
                link('admin:auth_user_changelist', 'admin:auth_user_add', 'Users', 'auth.view_user'),
                link('admin:auth_group_changelist', 'admin:auth_group_add', 'Roles', 'auth.view_group'),
                link('admin:testimonials_testimonial_changelist', 'admin:testimonials_testimonial_add', 'Testimonials', 'testimonials.view_testimonial'),
            ],
        },
        {
            'title': 'Content & SEO',
            'icon': 'content',
            'links': [
                link('admin:blog_blog_changelist', 'admin:blog_blog_add', 'Blog posts', 'blog.view_blog'),
                link('admin:blog_blogcategory_changelist', 'admin:blog_blogcategory_add', 'Blog categories', 'blog.view_blogcategory'),
                link('admin:blog_blogcomment_changelist', 'admin:blog_blogcomment_add', 'Comments', 'blog.view_blogcomment'),
                link('admin:blog_blogsubscription_changelist', 'admin:blog_blogsubscription_add', 'Subscribers', 'blog.view_blogsubscription'),
                link('admin:services_service_changelist', 'admin:services_service_add', 'Services', 'services.view_service'),
                link('admin:legal_legalpage_changelist', 'admin:legal_legalpage_add', 'Legal pages', 'legal.view_legalpage'),
                link('admin:legal_seosettings_changelist', 'admin:legal_seosettings_add', 'SEO settings', 'legal.view_seosettings'),
                link('admin:legal_sitemap_changelist', 'admin:legal_sitemap_add', 'Sitemap entries', 'legal.view_sitemap'),
            ],
        },
        {
            'title': 'Property management',
            'icon': 'management',
            'links': [
                link('admin:property_management_managedproperty_changelist', 'admin:property_management_managedproperty_add', 'Managed properties', 'property_management.view_managedproperty'),
                link('admin:property_management_tenant_changelist', 'admin:property_management_tenant_add', 'Tenants', 'property_management.view_tenant'),
                link('admin:property_management_rentpayment_changelist', 'admin:property_management_rentpayment_add', 'Rent payments', 'property_management.view_rentpayment'),
                link('admin:property_management_maintenanceschedule_changelist', 'admin:property_management_maintenanceschedule_add', 'Maintenance', 'property_management.view_maintenanceschedule'),
                report('analytics_dashboard', 'Analytics dashboard', 'property_management.view_managedproperty'),
            ],
        },
    ]

    for group in groups:
        group['links'] = [l for l in group['links'] if l]
    return [g for g in groups if g['links']]


def _recent_activity(limit=4, user=None):
    """Latest inquiries, bookings and testimonials, newest first.

    Only the kinds the viewer can open are included - a feed of links that lead
    to "permission denied" is worse than a shorter feed.
    """
    from contacts.models import Contact
    from listings.models import Booking
    from testimonials.models import Testimonial

    events = []

    if _can(user, 'contacts.view_contact'):
        for c in _safe(lambda: Contact.objects.order_by('-contact_date')[:limit], []):
            events.append({
                'when': c.contact_date,
                'kind': 'Inquiry',
                'text': f'{c.name} asked about {c.listing or "the team"}',
                'url': _reverse('admin:contacts_contact_change', c.pk),
            })
    if _can(user, 'listings.view_booking'):
        for b in _safe(lambda: Booking.objects.select_related('listing').order_by('-created_at')[:limit], []):
            events.append({
                'when': b.created_at,
                'kind': 'Booking',
                'text': (
                    f'{b.get_booking_type_display_custom()} · '
                    f'{b.listing.title if b.listing_id else "listing removed"}'
                ),
                'url': _reverse('admin:listings_booking_change', b.pk),
            })
    if _can(user, 'testimonials.view_testimonial'):
        for t in _safe(lambda: Testimonial.objects.order_by('-created_at')[:limit], []):
            events.append({
                'when': t.created_at,
                'kind': 'Testimonial',
                'text': f'{t.name} left a {t.rating} star review',
                'url': _reverse('admin:testimonials_testimonial_change', t.pk),
            })

    events = [e for e in events if e['when']]
    events.sort(key=lambda e: e['when'], reverse=True)
    return events[:limit]


def get_admin_dashboard_context(user=None):
    """Context consumed by ``templates/admin/custom_index.html``.

    ``user`` is used only to hide the header's shortcut buttons for staff who
    lack the matching permission - Django would otherwise render links that
    bounce them straight to a "permission denied" page.
    """
    last_week = timezone.now() - timedelta(days=7)
    context = {
        'kpis': _safe(lambda: _kpis(last_week, user), []),
        'attention_items': _safe(lambda: _attention_queue(user), []),
        'quick_action_groups': _safe(lambda: _quick_actions(user), []),
        'recent_activity': _safe(lambda: _recent_activity(user=user), []),
        'today': timezone.localdate(),
    }
    context.update(_safe(get_realtor_dashboard_context, {}))

    if user is not None:
        context.update({
            'can_add_listing': bool(_safe(
                lambda: user.has_perm('listings.add_listing'), False)),
            'can_change_seo': bool(_safe(
                lambda: user.has_perm('legal.change_seosettings'), False)),
            # The analytics dashboard is a staff report served from the public
            # URLconf, so its link is gated on the permission that owns the data
            # rather than on `is_staff` alone.
            'can_view_analytics': bool(_safe(
                lambda: user.has_perm('property_management.view_managedproperty'), False)),
        })
    return context


admin.site.index_template = 'admin/custom_index.html'

_original_index = admin.site.index


def custom_admin_index(request, extra_context=None):
    extra_context = extra_context or {}
    # Only build the dashboard for staff. Anonymous visitors never reach this
    # view (the admin wraps it in admin_site.admin_view), but the guard keeps
    # the intent explicit and avoids running the queries for non-staff users.
    if request.user.is_active and request.user.is_staff:
        extra_context.update(get_admin_dashboard_context(request.user))
    return _original_index(request, extra_context)


admin.site.index = custom_admin_index
