from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission to ensure users can only access conversations they're part of.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant of the conversation.
        """
        return request.user in obj.participants.all()


class IsMessageSenderOrConversationParticipant(permissions.BasePermission):
    """
    Permission to ensure users can only access messages from conversations
    they're part of.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the sender or a participant in the conversation.
        """
        # Check if user is the sender
        if obj.sender == request.user:
            return True
        
        # Check if user is a participant in the conversation
        return request.user in obj.conversation.participants.all()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Read permissions are allowed to any request,
        but write permissions are only allowed to the owner.
        """
        # Read permissions are allowed to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'sender'):
            return obj.sender == request.user
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        return False
