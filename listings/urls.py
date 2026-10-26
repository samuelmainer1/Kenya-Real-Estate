from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='listings'),
    path('search/', views.search, name='search'),
    path('booking/<int:listing_id>/', views.create_booking, name='listing_booking'),
    path('api/available-times/<int:listing_id>/', views.get_available_times, name='available_times'),
    path('api/available-dates/<int:listing_id>/', views.get_available_dates, name='available_dates'),
    path('<int:listing_id>/', views.listing_legacy_by_id, name='listing_legacy'),  # Legacy ID redirect
    path('<slug:slug>/', views.listing_by_slug, name='listing'),
]
