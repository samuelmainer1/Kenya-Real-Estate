from django.contrib import admin
from .models import LegalPage, SEOSettings, Sitemap

@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'page_type', 'is_active', 'last_updated', 'effective_date')
    list_filter = ('page_type', 'is_active', 'last_updated')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'page_type', 'effective_date', 'is_active')
        }),
        ('Content', {
            'fields': ('content',),
            'description': 'Use HTML formatting for better presentation'
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        js = ('admin/js/legal-admin.js',)
        css = {
            'all': ('admin/css/legal-admin.css',)
        }

@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_description', 'site_keywords')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url'),
            'classes': ('collapse',)
        }),
        ('Analytics & Tracking', {
            'fields': ('google_analytics_id', 'google_tag_manager_id', 'facebook_pixel_id'),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('organization_logo', 'default_image'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one SEO settings instance
        return not SEOSettings.objects.exists()

@admin.register(Sitemap)
class SitemapAdmin(admin.ModelAdmin):
    list_display = ('url', 'priority', 'changefreq', 'last_modified', 'is_active')
    list_filter = ('changefreq', 'priority', 'is_active')
    list_editable = ('priority', 'changefreq', 'is_active')
    search_fields = ('url',)
    
    actions = ['update_lastmod']
    
    def update_lastmod(self, request, queryset):
        from django.utils import timezone
        queryset.update(last_modified=timezone.now())
        self.message_user(request, f'Updated last modified date for {queryset.count()} entries.')
    update_lastmod.short_description = "Update last modified date"