from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('title', 'listing', 'name', 'rating', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'rating', 'is_featured', 'created_at', 'listing')
    search_fields = ('title', 'content', 'name', 'email', 'listing__title')
    list_editable = ('status', 'is_featured')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Details', {
            'fields': ('listing', 'client', 'name', 'email', 'rating', 'title', 'content')
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
