from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Permission to ensure only authenticated users who are participants
    can access, send, view, update, and delete messages in a conversation.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated before accessing any conversation.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a participant of the conversation.
        Only participants can view, send, update, and delete messages.
        """
        # Ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is a participant in the conversation
        return request.user in obj.participants.all()


class IsMessageSenderOrConversationParticipant(permissions.BasePermission):
    """
    Permission to ensure only authenticated users who are participants
    can access messages. Participants can send, view, update, and delete
    messages in their conversations.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated before accessing any message.
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the sender or a participant in the conversation.
        Only participants can view, send, update, and delete messages.
        """
        # Ensure user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
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
