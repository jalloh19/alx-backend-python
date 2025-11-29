"""
Views for messaging application.

Provides views to display messages and their edit history.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message


@login_required
def message_history(request, message_id):
    """
    Display the edit history of a specific message.
    
    Args:
        request: HTTP request object
        message_id: ID of the message to view history for
    
    Returns:
        Rendered template with message and its edit history
    """
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if request.user not in [message.sender, message.receiver]:
        return render(request, '403.html', status=403)
    
    # Get all edit history for this message
    history = message.history.all()
    
    context = {
        'message': message,
        'history': history,
    }
    
    return render(request, 'messaging/message_history.html', context)


@login_required
def message_history_json(request, message_id):
    """
    Return message edit history as JSON.
    
    Args:
        request: HTTP request object
        message_id: ID of the message to view history for
    
    Returns:
        JSON response with message history data
    """
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if request.user not in [message.sender, message.receiver]:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get all edit history for this message
    history = message.history.all()
    
    history_data = [
        {
            'id': entry.id,
            'old_content': entry.old_content,
            'edited_at': entry.edited_at.isoformat(),
            'edited_by': entry.edited_by.username if entry.edited_by else None,
        }
        for entry in history
    ]
    
    response_data = {
        'message_id': message.id,
        'current_content': message.content,
        'edited': message.edited,
        'history': history_data,
    }
    
    return JsonResponse(response_data)


@login_required
def user_messages(request):
    """
    Display all messages for the logged-in user.
    
    Shows messages sent and received, with indicators for edited messages.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered template with user's messages
    """
    sent_messages = Message.objects.filter(
        sender=request.user
    ).select_related('receiver')
    
    received_messages = Message.objects.filter(
        receiver=request.user
    ).select_related('sender')
    
    context = {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    }
    
    return render(request, 'messaging/user_messages.html', context)
