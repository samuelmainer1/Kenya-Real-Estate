from django.contrib import admin
from .models import Service

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_featured', 'is_active', 'order', 'created_at')
    list_filter = ('is_featured', 'is_active', 'created_at')
    search_fields = ('title', 'short_description', 'description')
    list_editable = ('is_featured', 'is_active', 'order')
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description', 'icon_class', 'image')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active', 'order'),
            'description': 'Featured services appear in footer and homepage'
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/services-admin.css',)
        }