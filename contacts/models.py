from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Contact(models.Model):
  listing = models.CharField(max_length=200)
  listing_id = models.IntegerField()
  name = models.CharField(max_length=200)
  email = models.CharField(max_length=100)
  phone = models.CharField(max_length=100)
  message = models.TextField(blank=True)
  contact_date = models.DateTimeField(default=timezone.now, blank=True)
  
  # Add foreign key relationships for better admin functionality
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='contacts')
  
  def __str__(self):
    return f"{self.name} - {self.listing}"
    
  class Meta:
    ordering = ['-contact_date']
    verbose_name = 'Contact Inquiry'
    verbose_name_plural = 'Contact Inquiries'