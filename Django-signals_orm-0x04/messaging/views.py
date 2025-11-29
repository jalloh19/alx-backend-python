"""
Views for messaging application.

Provides views to display messages and their edit history.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
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


@login_required
def delete_user(request):
    """
    Delete the current user's account along with all related data.
    
    This view handles account deletion with proper confirmation.
    When a user is deleted, the post_delete signal automatically
    cleans up all related messages, notifications, and message history.
    
    Args:
        request: HTTP request object
    
    Returns:
        GET: Rendered confirmation template
        POST: Redirects to home after deletion
    """
    if request.method == 'POST':
        # Get confirmation from user
        confirmation = request.POST.get('confirm_delete', '')
        
        if confirmation.lower() == 'delete':
            user = request.user
            username = user.username
            
            # Log the user out first
            logout(request)
            
            # Delete the user (signals will handle cleanup)
            user.delete()
            
            # Add success message
            django_messages.success(
                request,
                f'Account "{username}" has been successfully deleted.'
            )
            
            # Redirect to home or login page
            return redirect('/')
        else:
            # Invalid confirmation
            django_messages.error(
                request,
                'Invalid confirmation. Please type "DELETE" to confirm.'
            )
            return render(request, 'messaging/delete_user.html')
    
    # GET request - show confirmation page
    return render(request, 'messaging/delete_user.html')


@login_required
def unread_messages(request):
    """
    Display all unread messages for the logged-in user.
    
    Uses the custom UnreadMessagesManager to efficiently retrieve
    only unread messages with optimized field selection.
    
    Args:
        request: HTTP request object
    
    Returns:
        Rendered template with unread messages
    """
    # Use custom manager with .only() optimization
    messages_list = Message.unread.unread_for_user(request.user)
    
    context = {
        'unread_messages': messages_list,
        'unread_count': messages_list.count(),
    }
    
    return render(request, 'messaging/unread_messages.html', context)


@login_required
@cache_page(60)  # Cache for 60 seconds
def conversation_thread(request, message_id):
    """
    Display a threaded conversation starting from a specific message.
    
    Uses prefetch_related and select_related to optimize retrieval
    of the entire message thread with minimal database queries.
    Cached for 60 seconds to improve performance.
    
    Args:
        request: HTTP request object
        message_id: ID of the message to view thread for
    
    Returns:
        Rendered template with threaded conversation
    """
    # Get the message with optimized queries
    message = get_object_or_404(
        Message.objects.select_related(
            'sender',
            'receiver',
            'parent_message'
        ),
        id=message_id
    )
    
    # Check permission
    if request.user not in [message.sender, message.receiver]:
        return render(request, '403.html', status=403)
    
    # Get the entire thread with prefetch_related
    thread_messages = message.get_thread()
    
    # Mark message as read if current user is receiver
    if request.user == message.receiver and not message.read:
        message.mark_as_read()
    
    context = {
        'message': message,
        'thread_messages': thread_messages,
    }
    
    return render(request, 'messaging/conversation_thread.html', context)


@login_required
def mark_message_read(request, message_id):
    """
    Mark a specific message as read.
    
    Args:
        request: HTTP request object
        message_id: ID of the message to mark as read
    
    Returns:
        Redirect back to referrer or messages page
    """
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.mark_as_read()
    
    django_messages.success(request, 'Message marked as read.')
    
    # Redirect to referrer or default to messages page
    referrer = request.META.get('HTTP_REFERER', 'messaging:user_messages')
    return redirect(referrer)


@login_required
def reply_to_message(request, message_id):
    """
    Reply to a specific message, creating a threaded conversation.
    
    Args:
        request: HTTP request object
        message_id: ID of the message to reply to
    
    Returns:
        Rendered reply form or redirect after posting
    """
    parent = get_object_or_404(Message, id=message_id)
    
    # Check permission (must be sender or receiver of parent message)
    if request.user not in [parent.sender, parent.receiver]:
        return render(request, '403.html', status=403)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        
        if content:
            # Determine receiver (swap sender/receiver from parent)
            if request.user == parent.sender:
                receiver = parent.receiver
            else:
                receiver = parent.sender
            
            # Create reply message
            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                parent_message=parent
            )
            
            django_messages.success(request, 'Reply sent successfully.')
            return redirect(
                'messaging:conversation_thread',
                message_id=parent.id
            )
        else:
            django_messages.error(request, 'Reply content cannot be empty.')
    
    context = {
        'parent_message': parent,
    }
    
    return render(request, 'messaging/reply_form.html', context)
