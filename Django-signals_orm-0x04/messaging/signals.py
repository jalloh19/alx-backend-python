"""
Django signals for automatic notification creation.

This module contains signal handlers that automatically create
notifications when certain events occur (e.g., new messages).
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is created.
    
    This function is automatically triggered after a Message instance is saved.
    It creates a Notification for the receiver of the message, but only when
    a new message is created (not on updates).
    
    Args:
        sender: The model class (Message)
        instance: The actual Message instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    
    Flow:
        1. Message is created and saved
        2. post_save signal is triggered
        3. This handler checks if it's a new message (created=True)
        4. If new, creates a Notification for the receiver
        5. Notification is linked to both the user and the message
    """
    # Only create notification for newly created messages, not updates
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            is_read=False
        )
        print(f"✅ Notification created for {instance.receiver.username}: New message from {instance.sender.username}")
