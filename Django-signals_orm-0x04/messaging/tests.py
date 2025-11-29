"""
Tests for messaging and notification functionality.

Tests verify that:
1. Messages can be created successfully
2. Notifications are automatically created via signals
3. Notifications are linked correctly to users and messages
4. Multiple notifications work correctly
"""
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class MessageModelTest(TestCase):
    """Test cases for the Message model."""

    def setUp(self):
        """Create test users for messaging tests."""
        self.sender = User.objects.create_user(
            username='alice',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='bob',
            password='testpass123'
        )

    def test_message_creation(self):
        """Test that a message can be created successfully."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello Bob!"
        )
        
        self.assertIsNotNone(message.id)
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.content, "Hello Bob!")
        self.assertIsNotNone(message.timestamp)

    def test_message_str_representation(self):
        """Test the string representation of a message."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        str_repr = str(message)
        self.assertIn('alice', str_repr)
        self.assertIn('bob', str_repr)


class NotificationSignalTest(TestCase):
    """Test cases for automatic notification creation via signals."""

    def setUp(self):
        """Create test users for notification tests."""
        self.sender = User.objects.create_user(
            username='charlie',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='diana',
            password='testpass123'
        )

    def test_notification_created_on_message_save(self):
        """Test that a notification is automatically created when a message is saved."""
        # Initially, there should be no notifications
        self.assertEqual(Notification.objects.count(), 0)
        
        # Create a message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hey Diana, how are you?"
        )
        
        # Check that exactly one notification was created
        self.assertEqual(Notification.objects.count(), 1)
        
        # Verify the notification details
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_notification_not_created_on_message_update(self):
        """Test that updating a message doesn't create additional notifications."""
        # Create initial message (creates 1 notification)
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
        
        # Verify 1 notification exists
        self.assertEqual(Notification.objects.count(), 1)
        
        # Update the message
        message.content = "Updated content"
        message.save()
        
        # Verify still only 1 notification (no new one created)
        self.assertEqual(Notification.objects.count(), 1)

    def test_multiple_messages_create_multiple_notifications(self):
        """Test that multiple messages create multiple notifications."""
        # Create 3 messages
        for i in range(3):
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content=f"Message number {i+1}"
            )
        
        # Verify 3 notifications were created
        self.assertEqual(Notification.objects.count(), 3)
        
        # Verify all notifications are for the receiver
        notifications = Notification.objects.filter(user=self.receiver)
        self.assertEqual(notifications.count(), 3)

    def test_notification_for_correct_receiver(self):
        """Test that notification is created for the receiver, not sender."""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Test message"
        )
        
        # Check sender has no notifications
        sender_notifications = Notification.objects.filter(
            user=self.sender
        )
        self.assertEqual(sender_notifications.count(), 0)
        
        # Check receiver has 1 notification
        receiver_notifications = Notification.objects.filter(
            user=self.receiver
        )
        self.assertEqual(receiver_notifications.count(), 1)


class NotificationModelTest(TestCase):
    """Test cases for the Notification model."""

    def setUp(self):
        """Create test data for notification tests."""
        self.user1 = User.objects.create_user(
            username='eve',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='frank',
            password='testpass123'
        )
        
        self.message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for notification"
        )

    def test_notification_mark_as_read(self):
        """Test marking a notification as read."""
        notification = Notification.objects.get(user=self.user2)
        
        # Initially unread
        self.assertFalse(notification.is_read)
        
        # Mark as read
        notification.mark_as_read()
        
        # Verify it's now read
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_notification_str_representation(self):
        """Test the string representation of a notification."""
        notification = Notification.objects.get(user=self.user2)
        
        str_repr = str(notification)
        self.assertIn('frank', str_repr)
        self.assertIn('eve', str_repr)
        self.assertIn('unread', str_repr)

    def test_notification_ordering(self):
        """Test that notifications are ordered by creation time (newest first)."""
        # Create multiple messages/notifications
        for i in range(3):
            Message.objects.create(
                sender=self.user1,
                receiver=self.user2,
                content=f"Message {i}"
            )
        
        notifications = Notification.objects.filter(user=self.user2)
        
        # Verify they're in descending order (newest first)
        timestamps = [n.created_at for n in notifications]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))
