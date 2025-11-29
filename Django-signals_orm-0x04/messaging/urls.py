"""
URL configuration for messaging app.

Defines URL patterns for message views and history.
"""
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('messages/', views.user_messages, name='user_messages'),
    path('messages/unread/', views.unread_messages, name='unread_messages'),
    path('message/<int:message_id>/history/',
         views.message_history,
         name='message_history'),
    path('message/<int:message_id>/history/json/',
         views.message_history_json,
         name='message_history_json'),
    path('message/<int:message_id>/thread/',
         views.conversation_thread,
         name='conversation_thread'),
    path('message/<int:message_id>/read/',
         views.mark_message_read,
         name='mark_message_read'),
    path('message/<int:message_id>/reply/',
         views.reply_to_message,
         name='reply_to_message'),
    path('user/delete/', views.delete_user, name='delete_user'),
]
