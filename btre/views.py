"""Project-wide error handlers.

Django's default 404 handler only renders ``404.html`` when ``DEBUG == False``;
in development it shows the technical traceback page instead. Registering an
explicit ``handler404`` makes the branded page the single behaviour everywhere,
and guarantees a real HTTP 404 status (never a 200 "soft 404") which is what
search engines require in order to drop the URL from their index.
"""

from django.shortcuts import render


def page_not_found(request, exception=None, template_name='404.html'):
    """Return the branded 404 page with a genuine 404 status code."""
    return render(request, template_name, status=404)


def server_error(request, template_name='500.html'):
    """Return the branded 500 page with a genuine 500 status code."""
    try:
        return render(request, template_name, status=500)
    except Exception:  # pragma: no cover - template missing is not fatal
        from django.http import HttpResponse
        return HttpResponse('Server error', status=500)
