"""
URL configuration for messaging app.

Defines URL patterns for message views and history.
"""
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('messages/', views.user_messages, name='user_messages'),
    path('message/<int:message_id>/history/',
         views.message_history,
         name='message_history'),
    path('message/<int:message_id>/history/json/',
         views.message_history_json,
         name='message_history_json'),
]
