"""
Custom managers for the messaging app.

This module contains custom model managers that provide specialized
query methods for filtering and retrieving messages.
"""
from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager for filtering unread messages.
    
    This manager provides optimized queries for retrieving unread messages
    for a specific user. It uses .only() to limit the fields retrieved
    and select_related() to optimize foreign key lookups.
    
    Usage:
        # Get unread messages for a user
        unread = Message.unread.unread_for_user(request.user)
        
        # Count unread messages
        count = Message.unread.unread_for_user(request.user).count()
    """
    
    def unread_for_user(self, user):
        """
        Get all unread messages for a specific user.
        
        This method filters messages where:
        - The user is the receiver
        - The read status is False
        
        It uses optimization techniques:
        - .only() to retrieve only necessary fields
        - select_related() to reduce N+1 query problems
        
        Args:
            user: The User instance to get unread messages for
            
        Returns:
            QuerySet of unread Message objects with optimized field selection
            
        Example:
            >>> user = User.objects.get(username='alice')
            >>> unread = Message.unread.unread_for_user(user)
            >>> for msg in unread:
            ...     print(f"{msg.sender.username}: {msg.content}")
        """
        return self.filter(
            receiver=user,
            read=False
        ).select_related(
            'sender',
            'receiver'
        ).only(
            'id',
            'sender__username',
            'receiver__username',
            'content',
            'timestamp',
            'read'
        )
