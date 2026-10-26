from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from listings.models import Listing

class Testimonial(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='testimonials', null=True, blank=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials')
    name = models.CharField(max_length=100, help_text="Client's display name")
    email = models.EmailField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(default=False, max_length=200, help_text="Brief title for the testimonial")
    content = models.TextField(help_text="Detailed testimonial content")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
    
    def __str__(self):
        listing_title = self.listing.title if self.listing else "General"
        return f"{self.name} - {self.rating} stars - {listing_title}"
    
    def get_star_range(self):
        """Return range for displaying stars in templates"""
        return range(1, 6)
    
    def get_filled_stars(self):
        return range(self.rating)
    
    def get_empty_stars(self):
        return range(5 - self.rating)
