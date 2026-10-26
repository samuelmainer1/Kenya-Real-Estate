"""Single source of truth for the admin Control Centre navigation.

The Django admin only tells us *which models exist*; it cannot know that
"Managed properties" belongs next to "Rent payments", that "Listing alerts"
is a lead-capture tool rather than a listing, or that "SEO settings" is where
the site's metadata lives. This module encodes that editorial knowledge once,
and both the sidebar (``nav_sidebar.py``) and the dashboard quick actions
(``admin_dashboard.py``) read from it so they can never drift apart.

Two kinds of entry live here:

``nav`` sections
    Groups of **admin models**, referenced by ``app_label.ModelName`` and
    resolved against the admin's own ``available_apps`` list. Resolving
    against ``available_apps`` means a user only ever sees sections and
    models they have permission for, and a model removed from the admin
    simply disappears instead of raising ``NoReverseMatch``.

``site`` sections
    Groups of **public URLs**. These are the pages the admin content actually
    publishes, so being able to click straight from the Control Centre to the
    live page is the difference between guessing and verifying. They are
    rendered as a compact "Site shortcuts" panel rather than a wall of links.

Anything registered in the admin but not listed in ``NAV_SECTIONS`` is still
reachable: :func:`build_sidebar` appends an "Other admin models" section so a
future model can never become invisible.
"""

# Icons are names from ``btre/static/img/admin-icons.svg`` (a <symbol> sprite).
# Keeping them as ids avoids inlining SVG markup in every template row.

NAV_SECTIONS = [
    {
        'title': 'Overview',
        'icon': 'grid',
        'models': [],  # filled in by build_sidebar(): dashboard + audit log
        'extra_links': [
            ('Control Centre', 'admin:index', 'grid'),
        ],
    },
    {
        'title': 'Listings & bookings',
        'icon': 'home',
        'models': [
            'listings.Listing',
            'listings.Booking',
            'realtors.Realtor',
        ],
    },
    {
        'title': 'Clients & leads',
        'icon': 'users',
        'models': [
            'contacts.Contact',
            'listings.ListingSubscription',
            'testimonials.Testimonial',
        ],
    },
    {
        'title': 'Property management',
        'icon': 'building',
        'models': [
            'property_management.ManagedProperty',
            'property_management.Tenant',
            'property_management.RentPayment',
            'property_management.MaintenanceSchedule',
        ],
        # The occupancy/collection dashboard is a staff report, not a model, so
        # it has no changelist of its own and would otherwise be unreachable
        # except by typing its URL.
        'extra_links': [
            ('Analytics dashboard', 'analytics_dashboard', 'trending'),
        ],
    },
    {
        'title': 'Content & blog',
        'icon': 'file-text',
        'models': [
            'blog.Blog',
            'blog.BlogCategory',
            'blog.BlogComment',
            'blog.BlogSubscription',
            'services.Service',
            'legal.LegalPage',
        ],
    },
    {
        'title': 'Site settings',
        'icon': 'settings',
        'models': [
            'core.GlobalSettings',
            'legal.SEOSettings',
            'legal.Sitemap',
        ],
    },
    {
        'title': 'Users & access',
        'icon': 'shield',
        'models': [
            'auth.User',
            'auth.Group',
        ],
    },
    {
        'title': 'System',
        'icon': 'activity',
        'models': [
            'admin.LogEntry',
        ],
    },
]

# Public pages, grouped by what they are. ``url_name`` values must exist in the
# project's URLconfs; :func:`site_shortcut_groups` silently drops any that fail
# to reverse so a renamed or removed page cannot break the admin.
#
# ``perm`` (optional) names the admin permission that owns the page's content.
# A staff user cannot edit listings, so advertising the public listing pages to
# them is just noise - those shortcuts disappear without the permission.
SITE_SECTIONS = [
    {
        'title': 'Public pages',
        'icon': 'globe',
        'links': [
            ('Home', 'index', None),
            ('About', 'about', None),
            ('Listings', 'listings', 'listings.view_listing'),
            ('Property search', 'search', 'listings.view_listing'),
            ('Blog', 'blog_list', 'blog.view_blog'),
            ('Services', 'services', 'services.view_service'),
            ('Testimonials', 'testimonials:testimonials_list', 'testimonials.view_testimonial'),
            ('Property management', 'property_management', 'property_management.view_managedproperty'),
            ('Contact', 'contact_page', None),
            ('FAQ', 'faq', None),
        ],
    },
    {
        # Reports and tools that live on the public site but exist for staff.
        # They are not "public pages" in the marketing sense, yet every one of
        # them was previously reachable only by typing its URL.
        'title': 'Staff tools',
        'icon': 'trending',
        'links': [
            ('Analytics dashboard', 'analytics_dashboard', None),
            ('Tenant register', 'tenant_list', 'property_management.view_tenant'),
            ('Maintenance schedule', 'maintenance_list', 'property_management.view_maintenanceschedule'),
            ('Rent payments', 'rent_payments_list', 'property_management.view_rentpayment'),
        ],
    },
    {
        'title': 'Policies & machine files',
        'icon': 'file-text',
        'links': [
            ('Privacy policy', 'privacy_policy', None),
            ('Terms of service', 'terms_of_service', None),
            ('Sitemap.xml', 'sitemap', None),
            ('Robots.txt', 'robots', None),
        ],
    },
]
