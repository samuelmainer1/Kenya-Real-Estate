"""Context builders that feed the Control Centre sidebar and dashboard.

The sidebar is attached to *every* admin page (changelists, change forms, the
dashboard), so these lookups must be cheap. Model resolution reuses the admin's
own ``available_apps`` (already computed by ``AdminSite.each_context`` for the
current request), which means:

* no extra permission queries per render,
* users only ever see models they are allowed to open,
* the nav inherits Django's own caching of ``get_app_list``.
"""

from django.urls import NoReverseMatch, reverse

from btre.admin_nav import NAV_SECTIONS, SITE_SECTIONS


def _flatten_app_list(app_list):
    """Map ``'app_label.ModelName'`` to its admin ``model_dict``.

    ``app_list`` is the structure ``AdminSite.get_app_list`` returns, so each
    ``model_dict`` already carries ``name``, ``object_name``, ``admin_url``,
    ``add_url`` and ``perms`` for the *current user*.
    """
    index = {}
    for app in app_list or []:
        for model in app.get('models', []):
            index[f"{app['app_label']}.{model['object_name']}"] = model
    return index


def _live_count(model_key):
    """Count rows for the sidebar badges.

    Imported lazily and guarded: the sidebar renders on every admin page
    (including before a feature app has been migrated), and one missing table
    must not take the whole admin down.
    """
    app_label, model_name = model_key.split('.')
    try:
        from django.apps import apps as django_apps

        return django_apps.get_model(app_label, model_name).objects.count()
    except Exception:  # noqa: BLE001 - never break the sidebar
        return None


# Counting every table on every admin page would be wasteful; only models whose
# volume tells the owner something useful get a badge.
COUNTED_MODELS = {
    'listings.Listing',
    'listings.Booking',
    'contacts.Contact',
    'realtors.Realtor',
    'testimonials.Testimonial',
    'blog.Blog',
    'blog.BlogComment',
    'property_management.ManagedProperty',
    'property_management.MaintenanceSchedule',
    'auth.User',
}


def site_shortcut_groups(user=None):
    """Resolve ``SITE_SECTIONS`` to ``{'title', 'icon', 'links': [{label, url}]}``.

    Shortcuts whose ``perm`` the user lacks are dropped, so the Control Centre
    only advertises public pages that user can actually edit the content of.
    """
    groups = []
    for section in SITE_SECTIONS:
        links = []
        for label, url_name, perm in section['links']:
            if perm and user is not None and not user.has_perm(perm):
                continue
            try:
                links.append({'label': label, 'url': reverse(url_name)})
            except NoReverseMatch:
                # A renamed or removed page must not break the whole admin.
                continue
        if links:
            groups.append({'title': section['title'], 'icon': section['icon'], 'links': links})
    return groups


def build_sidebar(app_list, current_path):
    """Build the grouped sidebar sections.

    Returns a list of ``{'title', 'icon', 'active', 'links': [...]}`` dicts.
    Each link is ``{'label', 'url', 'icon', 'count', 'add_url', 'active'}``.
    """
    model_index = _flatten_app_list(app_list)
    used_keys = set()
    sections = []

    for section in NAV_SECTIONS:
        links = []

        for label, url_name, icon in section.get('extra_links', []):
            try:
                url = reverse(url_name)
            except NoReverseMatch:
                continue
            links.append({
                'label': label,
                'url': url,
                'icon': icon,
                'count': None,
                'add_url': None,
                'active': current_path == url,
            })

        for model_key in section['models']:
            model = model_index.get(model_key)
            if not model or not model.get('admin_url'):
                continue
            used_keys.add(model_key)
            links.append({
                'label': model['name'],
                'url': model['admin_url'],
                'icon': section['icon'],
                'count': _live_count(model_key) if model_key in COUNTED_MODELS else None,
                'add_url': model.get('add_url'),
                # A change form lives under the changelist URL, so a prefix
                # match keeps the right item highlighted while editing.
                'active': current_path.startswith(model['admin_url']),
            })

        if links:
            sections.append({
                'title': section['title'],
                'icon': section['icon'],
                'active': any(link['active'] for link in links),
                'links': links,
            })

    # Safety net: anything registered in the admin but absent from the config
    # stays reachable instead of silently disappearing after a refactor.
    leftovers = []
    for app in app_list or []:
        for model in app.get('models', []):
            key = f"{app['app_label']}.{model['object_name']}"
            if key in used_keys or not model.get('admin_url'):
                continue
            leftovers.append({
                'label': model['name'],
                'url': model['admin_url'],
                'icon': 'box',
                'count': None,
                'add_url': model.get('add_url'),
                'active': current_path.startswith(model['admin_url']),
            })
    if leftovers:
        sections.append({
            'title': 'Other admin models',
            'icon': 'box',
            'active': any(link['active'] for link in leftovers),
            'links': sorted(leftovers, key=lambda link: link['label'].lower()),
        })

    return sections


def sidebar_context(request, extra_context=None):
    """Add the sidebar context to an admin view's ``extra_context``.

    Called from the ``AdminSite.each_context`` hook in ``btre/admin_site.py`` so
    every admin page - not only the dashboard - gets the grouped navigation
    without needing a custom view per page.
    """
    context = extra_context or {}
    # Popups ("add related object") render without chrome, so skip the work.
    if not context.get('is_popup'):
        context['kc_sections'] = build_sidebar(context.get('available_apps'), request.path)
        context['kc_site_groups'] = site_shortcut_groups(getattr(request, 'user', None))
    return context

