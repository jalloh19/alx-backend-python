"""
Models for messaging and notifications system.

This module defines:
- Message: Messages sent between users
- Notification: Notifications created automatically when messages are received
"""
from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
    """
    Message model representing a message sent from one user to another.
    
    Fields:
        sender: User who sent the message
        receiver: User who receives the message
        content: The message text content
        timestamp: When the message was created
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

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['receiver', '-timestamp']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"


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
        return f"Notification for {self.user.username}: New message from {self.message.sender.username} ({status})"

    def mark_as_read(self):
        """Mark this notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
