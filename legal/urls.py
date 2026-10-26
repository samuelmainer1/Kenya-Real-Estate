from django.urls import path
from . import views

urlpatterns = [
    # /privacy-policy/ and /terms-of-service/ are served from the root urls.py
    # (via legal.views.privacy_policy / terms_of_service) - defined once only.
    # Sitemap and robots.txt are also routed at the site root.
    path('<slug:slug>/', views.legal_page, name='legal_page'),
]