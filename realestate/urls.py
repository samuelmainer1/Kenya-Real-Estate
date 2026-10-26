from testimonials import views as testimonial_views

urlpatterns = [
    # ... existing patterns
    path('testimonials/', include('testimonials.urls')),
    path('add-testimonial/<slug:slug>/', testimonial_views.add_testimonial, name='add_testimonial'),
    # ... other patterns
]
