"""
Django admin configuration for messaging models.

Provides a user-friendly interface to manage messages and notifications.
"""
from django.contrib import admin
from .models import Message, Notification


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Message model.
    
    Displays key information and provides filtering/searching capabilities.
    """
    list_display = (
        'id',
        'sender',
        'receiver',
        'content_preview',
        'timestamp'
    )
    list_filter = ('timestamp', 'sender', 'receiver')
    search_fields = ('sender__username', 'receiver__username', 'content')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def content_preview(self, obj):
        """Display first 50 characters of message content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = 'Content'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model.
    
    Displays notification details with filtering and actions.
    """
    list_display = (
        'id',
        'user',
        'message_sender',
        'is_read',
        'created_at'
    )
    list_filter = ('is_read', 'created_at', 'user')
    search_fields = ('user__username', 'message__sender__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    actions = ['mark_as_read', 'mark_as_unread']

    def message_sender(self, obj):
        """Display the sender of the related message."""
        return obj.message.sender.username
    
    message_sender.short_description = 'From'

    def mark_as_read(self, request, queryset):
        """Admin action to mark notifications as read."""
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            f'{updated} notification(s) marked as read.'
        )
    
    mark_as_read.short_description = 'Mark selected as read'

    def mark_as_unread(self, request, queryset):
        """Admin action to mark notifications as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            f'{updated} notification(s) marked as unread.'
        )
    
    mark_as_unread.short_description = 'Mark selected as unread'
