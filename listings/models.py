from django.db import models
from datetime import datetime
from realtors.models import Realtor
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth.models import User
import uuid
from django.urls import reverse

class ListingQuerySet(models.QuerySet):
    def public(self):
        """Published listings attached to admin-verified realtors."""
        return self.filter(is_published=True, realtor__is_verified=True)


class Listing(models.Model):
  PROPERTY_TYPES = [
    ('sale', 'For Sale'),
    ('rent', 'For Rent'),
    ('airbnb', 'Airbnb'),
  ]
  
  realtor = models.ForeignKey(Realtor, on_delete=models.DO_NOTHING)
  title = models.CharField(max_length=200)
  property_type = models.CharField(max_length=10, choices=PROPERTY_TYPES, default='sale')
  address = models.CharField(max_length=200)
  city = models.CharField(max_length=100)
  state = models.CharField(max_length=100)
  zipcode = models.CharField(max_length=20)
  description = models.TextField(blank=True)
  price = models.IntegerField()
  bedrooms = models.IntegerField()
  bathrooms = models.DecimalField(max_digits=2, decimal_places=1)
  garage = models.IntegerField(default=0)
  lot_size = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
  sqft = models.IntegerField(null=True, blank=True)
  photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
  photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
  photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
  photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
  photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
  photo_5 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
  photo_6 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
  is_published = models.BooleanField(default=True)
  list_date = models.DateTimeField(default=timezone.now, blank=True)
  slug = models.SlugField(unique=True, blank=True, null=True)
  amenities = models.JSONField(default=list, blank=True, help_text='List of amenities (school, market, hospital, etc)')
  latitude = models.FloatField(null=True, blank=True)
  longitude = models.FloatField(null=True, blank=True)

  objects = ListingQuerySet.as_manager()

  def save(self, *args, **kwargs):
    if not self.slug:
      base_slug = slugify(self.title) or 'listing'
      unique_slug = base_slug
      counter = 2
      # Allow listings to share the same title while keeping slugs (and URLs) unique.
      while Listing.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
        unique_slug = f"{base_slug}-{counter}"
        counter += 1
      self.slug = unique_slug
    super().save(*args, **kwargs)

  def get_absolute_url(self):
    return f"/listings/{self.slug}/"

  def __str__(self):
    return self.title

  def get_related_listings(self, limit=4):
    """Get related listings based on location, price, and features"""
    related = Listing.objects.public().exclude(id=self.id)
    
    # Priority 1: Same city and similar price range (±30%)
    price_min = self.price * 0.7
    price_max = self.price * 1.3
    
    city_and_price = related.filter(
        city__iexact=self.city,
        price__gte=price_min,
        price__lte=price_max
    )
    
    if city_and_price.count() >= limit:
        return city_and_price.order_by('-list_date')[:limit]
    
    # Priority 2: Same city, any price
    city_matches = related.filter(city__iexact=self.city)
    if city_matches.count() >= limit:
        return city_matches.order_by('-list_date')[:limit]
    
    # Priority 3: Same state and similar bedrooms
    state_and_bedrooms = related.filter(
        state__iexact=self.state,
        bedrooms=self.bedrooms
    )
    
    if state_and_bedrooms.count() >= limit:
        return state_and_bedrooms.order_by('-list_date')[:limit]
    
    # Priority 4: Same state, any features
    state_matches = related.filter(state__iexact=self.state)
    if state_matches.count() >= limit:
        return state_matches.order_by('-list_date')[:limit]
    
    # Fallback: Any recent listings
    return related.order_by('-list_date')[:limit]

class Booking(models.Model):
    BOOKING_TYPE_CHOICES = [
        ('viewing', 'Property Viewing'),
        ('airbnb', 'Airbnb Booking'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    client_email = models.EmailField(max_length=100, null=True, blank=True)
    client_phone = models.CharField(max_length=20, null=True, blank=True)

    # Booking type to differentiate between viewing and airbnb
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPE_CHOICES, default='viewing')

    # For regular viewings
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    # For Airbnb bookings
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    check_in_time = models.TimeField(null=True, blank=True, default='15:00')  # 3 PM default
    check_out_time = models.TimeField(null=True, blank=True, default='11:00')  # 11 AM default

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        if self.booking_type == 'airbnb':
            return f"Airbnb booking for {self.listing} by {self.client} from {self.check_in_date} to {self.check_out_date}"
        return f"Viewing for {self.listing} by {self.client} on {self.date} at {self.time}"

    def get_booking_type_display_custom(self):
        """Get human-readable booking type"""
        return dict(self.BOOKING_TYPE_CHOICES).get(self.booking_type, self.booking_type)

    def get_period_display(self):
        """Get formatted period for display"""
        if self.booking_type == 'airbnb':
            return f"{self.check_in_date} to {self.check_out_date}"
        return f"{self.date} at {self.time}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['listing', 'date', 'time'],
                name='unique_viewing_booking',
                condition=models.Q(booking_type='viewing')
            )
        ]

class ListingSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    def get_unsubscribe_url(self):
        return reverse('unsubscribe_listing', kwargs={'token': self.unsubscribe_token})
