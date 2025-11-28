import django_filters
from .models import Message, Conversation


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for messages.
    Allows filtering by conversation, sender, and time range.
    """
    conversation = django_filters.UUIDFilter(
        field_name='conversation__conversation_id',
        lookup_expr='exact'
    )
    sender = django_filters.UUIDFilter(
        field_name='sender__user_id',
        lookup_expr='exact'
    )
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains'
    )
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains'
    )
    sent_after = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte'
    )
    sent_before = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte'
    )
    date_range = django_filters.DateFromToRangeFilter(field_name='sent_at')

    class Meta:
        model = Message
        fields = [
            'conversation',
            'sender',
            'sender_username',
            'message_body',
            'sent_after',
            'sent_before',
            'date_range'
        ]


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for conversations.
    Allows filtering by participants and time range.
    """
    participant = django_filters.UUIDFilter(
        field_name='participants__user_id',
        lookup_expr='exact'
    )
    participant_username = django_filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains'
    )
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )

    class Meta:
        model = Conversation
        fields = [
            'participant',
            'participant_username',
            'created_after',
            'created_before'
        ]
