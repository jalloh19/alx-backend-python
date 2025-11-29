"""
Models for messaging and notifications system.

This module defines:
- Message: Messages sent between users with threading and read status
- Notification: Notifications created automatically when messages are received
- MessageHistory: History of message edits
"""
from django.db import models
from django.contrib.auth.models import User
from .managers import UnreadMessagesManager


class Message(models.Model):
    """
    Message model representing a message sent from one user to another.
    
    Supports threaded conversations via self-referential parent_message field
    and tracks read status for each message.
    
    Fields:
        sender: User who sent the message
        receiver: User who receives the message
        content: The message text content
        timestamp: When the message was created
        edited: Whether the message has been edited
        read: Whether the receiver has read the message
        parent_message: Reference to parent message for threaded replies
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent the message"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        help_text="User who receives the message"
    )
    content = models.TextField(
        help_text="The message content"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the message was created"
    )
    edited = models.BooleanField(
        default=False,
        help_text="Whether the message has been edited"
    )
    read = models.BooleanField(
        default=False,
        help_text="Whether the receiver has read the message"
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent message if this is a reply"
    )
    
    # Custom managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['receiver', '-timestamp']),
            models.Index(fields=['receiver', 'read']),
            models.Index(fields=['parent_message', '-timestamp']),
        ]

    def __str__(self):
        return (f"Message from {self.sender.username} to "
                f"{self.receiver.username} at {self.timestamp}")
    
    def get_thread(self):
        """
        Get all messages in this thread (message and all its replies).
        
        Uses prefetch_related to optimize retrieval of nested replies.
        
        Returns:
            QuerySet of all messages in the thread
        """
        if self.parent_message:
            # If this is a reply, get the root message's thread
            return self.parent_message.get_thread()
        
        # This is the root message, get all replies recursively
        return Message.objects.filter(
            models.Q(id=self.id) |
            models.Q(parent_message=self) |
            models.Q(parent_message__parent_message=self)
        ).select_related(
            'sender',
            'receiver',
            'parent_message'
        ).prefetch_related(
            'replies',
            'replies__replies'
        ).order_by('timestamp')
    
    def get_all_replies(self):
        """
        Recursively get all direct and nested replies to this message.
        
        Returns:
            QuerySet of all reply messages
        """
        return Message.objects.filter(
            parent_message=self
        ).select_related(
            'sender',
            'receiver'
        ).prefetch_related(
            'replies'
        ).order_by('timestamp')
    
    def is_reply(self):
        """Check if this message is a reply to another message."""
        return self.parent_message is not None
    
    def mark_as_read(self):
        """Mark this message as read."""
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])


class MessageHistory(models.Model):
    """
    MessageHistory model for storing previous versions of edited messages.
    
    Automatically created via pre_save signal when a message is edited.
    
    Fields:
        message: The message that was edited
        old_content: The content before the edit
        edited_at: When the edit occurred
        edited_by: User who made the edit
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="The message that was edited"
    )
    old_content = models.TextField(
        help_text="The content before the edit"
    )
    edited_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the edit occurred"
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='message_edits',
        help_text="User who made the edit"
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name = 'Message History'
        verbose_name_plural = 'Message Histories'
        indexes = [
            models.Index(fields=['message', '-edited_at']),
        ]

    def __str__(self):
        return (f"Edit of message {self.message.id} at "
                f"{self.edited_at.strftime('%Y-%m-%d %H:%M:%S')}")


class Notification(models.Model):
    """
    Notification model for storing user notifications.
    
    Automatically created via signals when a user receives a message.
    
    Fields:
        user: User who receives the notification
        message: The message that triggered the notification
        is_read: Whether the notification has been read
        created_at: When the notification was created
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who receives this notification"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The message that triggered this notification"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the notification was created"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        status = "read" if self.is_read else "unread"
        return (f"Notification for {self.user.username}: "
                f"New message from {self.message.sender.username} "
                f"({status})")

    def mark_as_read(self):
        """Mark this notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
