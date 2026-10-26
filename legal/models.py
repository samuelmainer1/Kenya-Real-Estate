from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

class LegalPage(models.Model):
    PAGE_TYPES = [
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms of Service'),
        ('cookie', 'Cookie Policy'),
        ('disclaimer', 'Disclaimer'),
        ('refund', 'Refund Policy'),
        ('dmca', 'DMCA Policy'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, unique=True)
    content = models.TextField(help_text="Full legal content")
    last_updated = models.DateTimeField(auto_now=True)
    effective_date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description")
    meta_keywords = models.CharField(max_length=255, blank=True, help_text="SEO keywords")
    
    class Meta:
        ordering = ['page_type']
        verbose_name = 'Legal Page'
        verbose_name_plural = 'Legal Pages'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = f"{self.title} | Kenya Realestate Platform"
        if not self.meta_description:
            # last_updated is auto_now, so it is None on the first insert.
            stamp = (self.last_updated or timezone.now()).strftime('%B %Y')
            self.meta_description = (
                f"Read our {self.get_page_type_display().lower()} on "
                f"Kenya Realestate Platform. Updated {stamp}."
            )
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('legal_page', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title

class SEOSettings(models.Model):
    """Global SEO settings for the website"""
    site_name = models.CharField(max_length=100, default="Kenya Realestate Platform")
    site_description = models.CharField(
        max_length=160,
        default="Kenya Realestate Platform — buy, rent, and manage verified properties across Kenya."
    )
    site_keywords = models.TextField(
        default="Kenya real estate platform, property for sale Kenya, houses for rent Nairobi, Airbnb Kenya, property management Kenya"
    )
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    
    # Contact Info
    phone = models.CharField(max_length=20, default="+254 722 359 298")
    email = models.EmailField(default="samuelmainer@gmail.com")
    address = models.CharField(max_length=200, default="Nextgen Mall, Mombasa Road, Nairobi")
    
    # Analytics
    google_analytics_id = models.CharField(max_length=20, blank=True, help_text="GA4 Measurement ID")
    google_tag_manager_id = models.CharField(max_length=20, blank=True, help_text="GTM Container ID")
    facebook_pixel_id = models.CharField(max_length=20, blank=True)
    
    # Schema.org
    organization_logo = models.ImageField(upload_to='seo/', blank=True)
    default_image = models.ImageField(upload_to='seo/', blank=True, help_text="Default OG image")
    
    class Meta:
        verbose_name = 'SEO Settings'
        verbose_name_plural = 'SEO Settings'
    
    def __str__(self):
        return f"SEO Settings for {self.site_name}"

class Sitemap(models.Model):
    """Dynamic sitemap entries"""
    url = models.CharField(max_length=200)
    priority = models.DecimalField(max_digits=2, decimal_places=1, default=0.5)
    changefreq = models.CharField(max_length=10, choices=[
        ('always', 'Always'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('never', 'Never'),
    ], default='weekly')
    last_modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-priority', 'url']
    
    def __str__(self):
        return self.url