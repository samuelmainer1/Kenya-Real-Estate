from django.contrib import admin
from .models import Blog, BlogCategory, BlogComment, BlogSubscription
from django.utils import timezone
from django.utils.html import format_html

@admin.action(description='Publish selected blogs')
def make_published(modeladmin, request, queryset):
    queryset.update(published=True)

@admin.action(description='Unpublish selected blogs')
def make_unpublished(modeladmin, request, queryset):
    queryset.update(published=False)

@admin.action(description='Publish scheduled blogs now')
def publish_scheduled_now(modeladmin, request, queryset):
    now = timezone.now()
    scheduled_blogs = queryset.filter(scheduled_at__lte=now, published=False)
    count = scheduled_blogs.update(published=True)
    modeladmin.message_user(request, f'{count} scheduled blog(s) published successfully.')

class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'posted_at', 'read_time', 'published', 'scheduled_status', 'scheduled_at')
    search_fields = ('title', 'short_description', 'description')
    list_filter = ('category', 'author', 'posted_at', 'published', 'scheduled_at')
    actions = [make_published, make_unpublished, publish_scheduled_now]
    fieldsets = (
        (None, {'fields': ('title', 'image', 'short_description', 'description', 'author', 'category', 'read_time')}),
        ('Publishing', {'fields': ('published', 'scheduled_at', 'slug')}),
    )
    
    def scheduled_status(self, obj):
        if not obj.scheduled_at:
            return '-'
        
        now = timezone.now()
        if obj.scheduled_at <= now and not obj.published:
            return format_html('<span style="color: red;">Ready to publish</span>')
        elif obj.scheduled_at <= now and obj.published:
            return format_html('<span style="color: green;">Published</span>')
        else:
            return format_html('<span style="color: orange;">Scheduled</span>')
    
    scheduled_status.short_description = 'Schedule Status'
    
    def save_model(self, request, obj, form, change):
        # Check if blog should be auto-published when saving
        if obj.scheduled_at and obj.scheduled_at <= timezone.now() and not obj.published:
            obj.published = True
        super().save_model(request, obj, form, change)

class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'created_at')
    search_fields = ('content',)

class BlogSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)

admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
admin.site.register(BlogSubscription, BlogSubscriptionAdmin)
