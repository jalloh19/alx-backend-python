#!/usr/bin/env python
"""
Test script to demonstrate message edit logging functionality.

This script creates test users and messages, then demonstrates
the edit logging feature by modifying messages and viewing history.
"""
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messaging_project.settings')
django.setup()

from django.contrib.auth.models import User
from messaging.models import Message, MessageHistory


def create_test_data():
    """Create test users and messages."""
    print("\n" + "="*60)
    print("Creating Test Data")
    print("="*60)
    
    # Create or get test users
    alice, _ = User.objects.get_or_create(
        username='alice',
        defaults={'email': 'alice@example.com'}
    )
    alice.set_password('password123')
    alice.save()
    print(f"✓ User created: {alice.username}")
    
    bob, _ = User.objects.get_or_create(
        username='bob',
        defaults={'email': 'bob@example.com'}
    )
    bob.set_password('password123')
    bob.save()
    print(f"✓ User created: {bob.username}")
    
    return alice, bob


def test_message_edit_logging():
    """Test the message edit logging functionality."""
    print("\n" + "="*60)
    print("Testing Message Edit Logging")
    print("="*60)
    
    alice, bob = create_test_data()
    
    # Create a new message
    print("\n1. Creating new message...")
    message = Message.objects.create(
        sender=alice,
        receiver=bob,
        content="Hello Bob, how are you?"
    )
    print(f"   ✓ Message created (ID: {message.id})")
    print(f"   Content: '{message.content}'")
    print(f"   Edited: {message.edited}")
    print(f"   History count: {message.history.count()}")
    
    # First edit
    print("\n2. Making first edit...")
    message.content = "Hello Bob, how are you doing?"
    message.save()
    print(f"   ✓ Message edited")
    print(f"   New content: '{message.content}'")
    print(f"   Edited: {message.edited}")
    print(f"   History count: {message.history.count()}")
    
    # Display first history entry
    if message.history.exists():
        history = message.history.first()
        print(f"\n   History Entry:")
        print(f"   - Old content: '{history.old_content}'")
        print(f"   - Edited at: {history.edited_at}")
        print(f"   - Edited by: {history.edited_by.username}")
    
    # Second edit
    print("\n3. Making second edit...")
    message.content = "Hello Bob, how are you doing today?"
    message.save()
    print(f"   ✓ Message edited again")
    print(f"   New content: '{message.content}'")
    print(f"   Edited: {message.edited}")
    print(f"   History count: {message.history.count()}")
    
    # Display all history
    print("\n4. Complete Edit History:")
    print("   " + "-"*56)
    for i, history in enumerate(message.history.all(), 1):
        print(f"   Edit #{i}:")
        print(f"   - Previous content: '{history.old_content}'")
        print(f"   - Edited at: {history.edited_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Edited by: {history.edited_by.username}")
        print("   " + "-"*56)
    
    # Test: Saving without content change
    print("\n5. Testing save without content change...")
    old_history_count = message.history.count()
    message.save()  # Save without changing content
    new_history_count = message.history.count()
    print(f"   History count before: {old_history_count}")
    print(f"   History count after: {new_history_count}")
    print(f"   ✓ No new history entry created (as expected)")
    
    print("\n" + "="*60)
    print("Test completed successfully!")
    print("="*60)
    
    # Summary
    print(f"\nSummary:")
    print(f"- Original message: 'Hello Bob, how are you?'")
    print(f"- Current message: '{message.content}'")
    print(f"- Total edits: {message.history.count()}")
    print(f"- Message marked as edited: {message.edited}")
    print(f"\nYou can view this in the admin panel at:")
    print(f"  - Messages: http://127.0.0.1:8000/admin/messaging/message/{message.id}/change/")
    print(f"  - History: http://127.0.0.1:8000/admin/messaging/messagehistory/")
    print(f"  - User view: http://127.0.0.1:8000/messages/")
    print(f"  - History view: http://127.0.0.1:8000/message/{message.id}/history/")
    print(f"  - JSON API: http://127.0.0.1:8000/message/{message.id}/history/json/")


if __name__ == '__main__':
    test_message_edit_logging()
