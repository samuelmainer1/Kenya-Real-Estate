from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Canonical contact page (also linked as /contact/ from pages.urls).
    path('', views.contact, name='contact'),
    # Legacy alias kept for old links and bookmarks.
    path('contact/',
         RedirectView.as_view(pattern_name='contact', permanent=True),
         name='contact_page'),
]
