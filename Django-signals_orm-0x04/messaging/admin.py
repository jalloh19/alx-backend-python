"""
Django admin configuration for messaging models.

Provides a user-friendly interface to manage messages and notifications.
"""
from django.contrib import admin
from .models import Message, Notification, MessageHistory


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
        'timestamp',
        'edited'
    )
    list_filter = ('timestamp', 'sender', 'receiver')
    search_fields = ('sender__username', 'receiver__username', 'content')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def content_preview(self, obj):
        """Display first 50 characters of message content."""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    
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


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for MessageHistory model.
    
    Displays edit history with read-only access.
    """
    list_display = (
        'id',
        'message_id_display',
        'message_sender',
        'old_content_preview',
        'edited_by',
        'edited_at'
    )
    list_filter = ('edited_at', 'edited_by')
    search_fields = (
        'message__sender__username',
        'message__receiver__username',
        'old_content',
        'edited_by__username'
    )
    date_hierarchy = 'edited_at'
    readonly_fields = (
        'message',
        'old_content',
        'edited_by',
        'edited_at'
    )
    ordering = ('-edited_at',)

    def has_add_permission(self, request):
        """Prevent manual creation of history records."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion for cleanup purposes."""
        return True

    def message_id_display(self, obj):
        """Display the message ID."""
        return obj.message.id
    
    message_id_display.short_description = 'Message ID'

    def message_sender(self, obj):
        """Display the sender of the related message."""
        return obj.message.sender.username
    
    message_sender.short_description = 'Message From'

    def old_content_preview(self, obj):
        """Display first 50 characters of old content."""
        max_len = 50
        if len(obj.old_content) > max_len:
            return obj.old_content[:max_len] + '...'
        return obj.old_content
    
    old_content_preview.short_description = 'Previous Content'
