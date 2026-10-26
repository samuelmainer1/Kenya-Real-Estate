from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=300, help_text="Brief description for cards and footer")
    description = models.TextField(help_text="Full description for service detail page")
    icon_class = models.CharField(max_length=100, default='fas fa-home', help_text="FontAwesome icon class (e.g., fas fa-home)")
    image = models.ImageField(upload_to='services/%Y/%m/%d/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, help_text="Show in footer and homepage")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (leave blank to use title)")
    meta_description = models.CharField(max_length=300, blank=True, help_text="SEO description")
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.short_description
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title