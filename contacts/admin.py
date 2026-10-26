from django.contrib import admin

from .models import Contact

class ContactAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'email', 'phone', 'listing', 'listing_id', 'contact_date', 'user', 'has_message')
  list_display_links = ('id', 'name')
  list_filter = ('contact_date', 'listing_id', 'user')
  search_fields = ('name', 'email', 'phone', 'listing', 'message')
  list_per_page = 25
  readonly_fields = ('contact_date',)
  ordering = ('-contact_date',)
  
  def has_message(self, obj):
    return bool(obj.message.strip()) if obj.message else False
  has_message.boolean = True
  has_message.short_description = 'Has Message'
  
  fieldsets = (
    ('Contact Information', {
      'fields': ('name', 'email', 'phone')
    }),
    ('Property Information', {
      'fields': ('listing', 'listing_id')
    }),
    ('Message Details', {
      'fields': ('message', 'contact_date'),
      'classes': ('collapse',)
    }),
    ('User Information', {
      'fields': ('user',),
      'classes': ('collapse',)
    }),
  )

admin.site.register(Contact, ContactAdmin)
