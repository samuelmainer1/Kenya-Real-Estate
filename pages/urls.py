from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('contact/', views.contact, name='contact_page'),
    path('footer-subscribe/', views.footer_subscribe, name='footer_subscribe'),
]
