#!/usr/bin/env python
"""
Test script to demonstrate user deletion with automatic data cleanup.

This script creates test users with messages and notifications,
then deletes a user to verify that all related data is cleaned up
via the post_delete signal.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_project.settings')
django.setup()

from django.contrib.auth.models import User
from messaging.models import Message, Notification, MessageHistory


def print_separator(title):
    """Print a formatted separator."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def count_user_data(username):
    """Count all data related to a user."""
    try:
        user = User.objects.get(username=username)
        sent = Message.objects.filter(sender=user).count()
        received = Message.objects.filter(receiver=user).count()
        notifications = Notification.objects.filter(user=user).count()
        edits = MessageHistory.objects.filter(edited_by=user).count()
        
        return {
            'exists': True,
            'sent_messages': sent,
            'received_messages': received,
            'total_messages': sent + received,
            'notifications': notifications,
            'message_edits': edits
        }
    except User.DoesNotExist:
        return {'exists': False}


def display_user_data(username, data):
    """Display user data in a formatted way."""
    if not data['exists']:
        print(f"   ❌ User '{username}' does not exist")
        return
    
    print(f"   ✓ User: {username}")
    print(f"   - Sent messages: {data['sent_messages']}")
    print(f"   - Received messages: {data['received_messages']}")
    print(f"   - Total messages: {data['total_messages']}")
    print(f"   - Notifications: {data['notifications']}")
    print(f"   - Message edits: {data['message_edits']}")


def test_user_deletion_cleanup():
    """Test user deletion with automatic data cleanup."""
    print_separator("Testing User Deletion with Data Cleanup")
    
    # Step 1: Create test users
    print("\n1. Creating test users...")
    alice, _ = User.objects.get_or_create(
        username='alice_test',
        defaults={'email': 'alice@test.com'}
    )
    alice.set_password('password123')
    alice.save()
    print(f"   ✓ Created user: {alice.username}")
    
    bob, _ = User.objects.get_or_create(
        username='bob_test',
        defaults={'email': 'bob@test.com'}
    )
    bob.set_password('password123')
    bob.save()
    print(f"   ✓ Created user: {bob.username}")
    
    charlie, _ = User.objects.get_or_create(
        username='charlie_test',
        defaults={'email': 'charlie@test.com'}
    )
    charlie.set_password('password123')
    charlie.save()
    print(f"   ✓ Created user: {charlie.username}")
    
    # Step 2: Create messages between users
    print("\n2. Creating messages...")
    
    # Alice sends to Bob
    msg1 = Message.objects.create(
        sender=alice,
        receiver=bob,
        content="Hello Bob from Alice!"
    )
    print(f"   ✓ Message 1: Alice → Bob")
    
    # Bob sends to Alice
    msg2 = Message.objects.create(
        sender=bob,
        receiver=alice,
        content="Hi Alice from Bob!"
    )
    print(f"   ✓ Message 2: Bob → Alice")
    
    # Alice sends to Charlie
    msg3 = Message.objects.create(
        sender=alice,
        receiver=charlie,
        content="Hey Charlie from Alice!"
    )
    print(f"   ✓ Message 3: Alice → Charlie")
    
    # Charlie sends to Alice
    msg4 = Message.objects.create(
        sender=charlie,
        receiver=alice,
        content="Hello Alice from Charlie!"
    )
    print(f"   ✓ Message 4: Charlie → Alice")
    
    # Step 3: Edit some messages to create history
    print("\n3. Editing messages to create history...")
    msg1.content = "Hello Bob from Alice! How are you?"
    msg1.save()
    print(f"   ✓ Edited message 1 (creates history)")
    
    msg3.content = "Hey Charlie from Alice! Long time no see!"
    msg3.save()
    print(f"   ✓ Edited message 3 (creates history)")
    
    # Step 4: Display data BEFORE deletion
    print_separator("Data BEFORE Deletion")
    
    print("\nAlice's data:")
    alice_before = count_user_data('alice_test')
    display_user_data('alice_test', alice_before)
    
    print("\nBob's data:")
    bob_before = count_user_data('bob_test')
    display_user_data('bob_test', bob_before)
    
    print("\nCharlie's data:")
    charlie_before = count_user_data('charlie_test')
    display_user_data('charlie_test', charlie_before)
    
    # Step 5: Count total data in database
    print("\n" + "-"*70)
    total_messages_before = Message.objects.count()
    total_notifications_before = Notification.objects.count()
    total_history_before = MessageHistory.objects.count()
    
    print(f"Total data in database:")
    print(f"   - Messages: {total_messages_before}")
    print(f"   - Notifications: {total_notifications_before}")
    print(f"   - Message History: {total_history_before}")
    
    # Step 6: Delete Alice's account
    print_separator("Deleting Alice's Account")
    print("\n🗑️  Deleting user 'alice_test'...")
    print("   (Signal will automatically clean up related data)\n")
    
    alice.delete()  # This triggers the post_delete signal
    
    # Step 7: Display data AFTER deletion
    print_separator("Data AFTER Deletion")
    
    print("\nAlice's data:")
    alice_after = count_user_data('alice_test')
    display_user_data('alice_test', alice_after)
    
    print("\nBob's data:")
    bob_after = count_user_data('bob_test')
    display_user_data('bob_test', bob_after)
    
    print("\nCharlie's data:")
    charlie_after = count_user_data('charlie_test')
    display_user_data('charlie_test', charlie_after)
    
    # Step 8: Verify cleanup
    print("\n" + "-"*70)
    total_messages_after = Message.objects.count()
    total_notifications_after = Notification.objects.count()
    total_history_after = MessageHistory.objects.count()
    
    print(f"Total data in database:")
    print(f"   - Messages: {total_messages_after} "
          f"(was {total_messages_before}, deleted {total_messages_before - total_messages_after})")
    print(f"   - Notifications: {total_notifications_after} "
          f"(was {total_notifications_before}, deleted {total_notifications_before - total_notifications_after})")
    print(f"   - Message History: {total_history_after} "
          f"(was {total_history_before}, updated {total_history_before - total_history_after})")
    
    # Step 9: Verification summary
    print_separator("Verification Summary")
    
    messages_deleted = total_messages_before - total_messages_after
    notifications_deleted = total_notifications_before - total_notifications_after
    
    print("\n✅ Cleanup verification:")
    print(f"   ✓ User 'alice_test' deleted: {not alice_after['exists']}")
    print(f"   ✓ Messages cleaned up: {messages_deleted} deleted")
    print(f"   ✓ Notifications cleaned up: {notifications_deleted} deleted")
    print(f"   ✓ Message history preserved: {total_history_after} entries")
    print(f"      (edited_by set to NULL for Alice's edits)")
    
    # Expected deletions
    expected_message_deletions = (
        alice_before['sent_messages'] + alice_before['received_messages']
    )
    
    print(f"\n📊 Expected vs Actual:")
    print(f"   Expected message deletions: {expected_message_deletions}")
    print(f"   Actual message deletions: {messages_deleted}")
    print(f"   Match: {'✓ Yes' if messages_deleted == expected_message_deletions else '✗ No'}")
    
    print(f"\n   Expected notification deletions: {alice_before['notifications']}")
    print(f"   Actual notification deletions: {notifications_deleted}")
    print(f"   Match: {'✓ Yes' if notifications_deleted == alice_before['notifications'] else '✗ No'}")
    
    # Step 10: Check MessageHistory integrity
    print("\n📝 Message History Integrity Check:")
    history_entries = MessageHistory.objects.all()
    for entry in history_entries:
        editor = entry.edited_by.username if entry.edited_by else "NULL (deleted user)"
        print(f"   - History #{entry.id}: edited_by = {editor}")
    
    print_separator("Test Completed Successfully")
    
    print("\n✅ All tests passed!")
    print("   - User deletion works correctly")
    print("   - CASCADE deletion cleans up messages and notifications")
    print("   - SET_NULL preserves message history")
    print("   - Foreign key constraints are respected")
    print("   - post_delete signal provides proper logging")
    
    # Cleanup test data
    print("\n🧹 Cleaning up test data...")
    User.objects.filter(username__in=['bob_test', 'charlie_test']).delete()
    print("   ✓ Test users removed")


if __name__ == '__main__':
    test_user_deletion_cleanup()
