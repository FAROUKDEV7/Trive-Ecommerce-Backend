from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Customer Info', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message Content', {
            'fields': ('subject', 'message', 'created_at')
        }),
        ('Admin Actions', {
            'fields': ('status', 'admin_reply')
        }),
    )
