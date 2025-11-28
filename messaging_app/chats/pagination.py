from rest_framework.pagination import PageNumberPagination


class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Returns 20 messages per page.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationPagination(PageNumberPagination):
    """
    Custom pagination class for conversations.
    Returns 10 conversations per page.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
