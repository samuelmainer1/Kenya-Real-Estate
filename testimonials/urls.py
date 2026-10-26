from django.urls import path
from . import views

app_name = 'testimonials'

urlpatterns = [
    path('', views.testimonials_list, name='testimonials_list'),
    path('listing/<slug:slug>/', views.listing_testimonials, name='listing_testimonials'),
    path('add/<slug:slug>/', views.add_testimonial, name='add_testimonial'),
]
