from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides list, create, retrieve, update, and delete actions.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__username', 'participants__email']
    ordering_fields = ['created_at']

    def get_queryset(self):
        """
        Filter conversations to only include those where the user is a participant.
        """
        user = self.request.user
        return Conversation.objects.filter(participants=user)

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with participants.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Add participants from request
        participant_ids = request.data.get('participant_ids', [])
        if participant_ids:
            conversation.participants.set(participant_ids)
        
        # Add the current user as a participant
        conversation.participants.add(request.user)
        
        return Response(
            self.get_serializer(conversation).data,
            status=status.HTTP_201_CREATED
        )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides list, create, retrieve, update, and delete actions.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        """
        Filter messages to only include those in conversations where the user is a participant.
        """
        user = self.request.user
        return Message.objects.filter(
            conversation__participants=user
        ).order_by('-sent_at')

    def create(self, request, *args, **kwargs):
        """
        Send a new message to an existing conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the sender to the current user
        message = serializer.save(sender=request.user)
        
        return Response(
            self.get_serializer(message).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """
        Get all messages for a specific conversation.
        Usage: /messages/by_conversation/?conversation_id=<uuid>
        """
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        messages = self.get_queryset().filter(conversation_id=conversation_id)
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
