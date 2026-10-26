from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import uuid
from django.urls import reverse


class BlogCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='blog_images/')
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(null=True, blank=True, help_text='Schedule blog for future publishing')
    read_time = models.PositiveIntegerField(help_text='Estimated read time in minutes')
    likes = models.ManyToManyField(User, related_name='blog_likes', blank=True)
    published = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, null=True, blank=True)


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        was_published = False
        if self.pk:
            old_instance = Blog.objects.get(pk=self.pk)
            was_published = old_instance.published
        
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-publish if scheduled_at is in the past and not already published
        if self.scheduled_at and self.scheduled_at <= timezone.now() and not self.published:
            self.published = True
        
        super().save(*args, **kwargs)
        
        # Send notification if blog was just published
        if self.published and not was_published:
            from .utils import send_blog_notification
            send_blog_notification(self)


class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.blog}'


class BlogSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
    
    def get_unsubscribe_url(self):
        return reverse('unsubscribe', kwargs={'token': self.unsubscribe_token})
