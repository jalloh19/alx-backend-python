"""
Application configuration for the messaging app.

This module registers the signals when the app is ready.
"""
from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """
    Configuration for the messaging application.
    
    Registers signal handlers when the app is ready to ensure
    automatic notification creation works properly.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "messaging"

    def ready(self):
        """
        Import signal handlers when the app is ready.
        
        This method is called by Django when the application is fully loaded.
        It imports the signals module which registers all signal handlers
        using the @receiver decorator.
        """
        import messaging.signals  # noqa: F401
