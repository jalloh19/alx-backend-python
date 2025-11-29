"""
Django signals for automatic notification creation.

This module contains signal handlers that automatically create
notifications when certain events occur (e.g., new messages).
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory


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
        print(f"✅ Notification created for {instance.receiver.username}: "
              f"New message from {instance.sender.username}")


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler that logs the old content when a message is edited.
    
    This function is triggered before a Message instance is saved.
    It checks if the message already exists in the database and if the
    content has changed. If so, it saves the old content to MessageHistory
    and marks the message as edited.
    
    Args:
        sender: The model class (Message)
        instance: The Message instance being saved
        **kwargs: Additional keyword arguments
    
    Flow:
        1. Message is about to be saved (updated)
        2. pre_save signal is triggered
        3. This handler checks if message exists and content changed
        4. If content changed, creates MessageHistory with old content
        5. Marks the message as edited
    """
    # Only process if the message already exists (i.e., it's an update)
    if instance.pk:
        try:
            # Fetch the old version from database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has actually changed
            if old_message.content != instance.content:
                # Create history record with old content
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender
                )
                
                # Mark the message as edited
                instance.edited = True
                
                print(f"📝 Message edit logged: Message {instance.pk} "
                      f"by {instance.sender.username}")
        except Message.DoesNotExist:
            # Message doesn't exist yet, nothing to log
            pass
