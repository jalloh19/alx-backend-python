# Django Signals ORM - 0x04

## Project Overview

This project demonstrates **Django Signals** for automatic notification creation when users receive messages. It showcases how signals enable decoupled, event-driven programming in Django applications.

## 🎯 Objective

Automatically notify users when they receive a new message using Django's signal system.

## 📋 What Was Implemented

### 1. **Message Model** (`messaging/models.py`)
- Stores messages between users
- Fields: `sender`, `receiver`, `content`, `timestamp`
- Relationships: ForeignKey to User model

### 2. **Notification Model** (`messaging/models.py`)
- Stores user notifications
- Fields: `user`, `message`, `is_read`, `created_at`
- Auto-created via signals when messages are received
- Method: `mark_as_read()` to update notification status

### 3. **Signal Handler** (`messaging/signals.py`)
- Uses `@receiver(post_save, sender=Message)`
- Automatically creates Notification when Message is created
- Only triggers on new messages (not updates)
- Links notification to receiver and message

### 4. **App Configuration** (`messaging/apps.py`)
- Registers signals in `ready()` method
- Ensures signals are connected when app loads

### 5. **Admin Interface** (`messaging/admin.py`)
- User-friendly management of messages
- Notification management with read/unread actions
- Filtering, searching, and bulk operations

### 6. **Comprehensive Tests** (`messaging/tests.py`)
- Tests message creation
- Tests automatic notification creation
- Tests that updates don't create duplicate notifications
- Tests multiple messages and notifications
- All 9 tests passing ✅

## 🔧 How It Works

```
┌─────────────────────────────────────────────────────┐
│  User A sends message to User B                     │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Message.objects.create(                            │
│      sender=user_a,                                 │
│      receiver=user_b,                               │
│      content="Hello!"                               │
│  )                                                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Django saves Message to database                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  post_save signal is triggered                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  create_notification_on_message() handler runs      │
│  - Checks if message is new (created=True)          │
│  - Creates Notification for receiver                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  Notification.objects.create(                       │
│      user=user_b,                                   │
│      message=message_instance,                      │
│      is_read=False                                  │
│  )                                                  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  User B can now see notification of new message     │
└─────────────────────────────────────────────────────┘
```

## 🚀 Setup Instructions

### 1. Navigate to project directory
```bash
cd Django-signals_orm-0x04
```

### 2. Run migrations (already done)
```bash
python manage.py migrate
```

### 3. Create a superuser for admin access
```bash
python manage.py createsuperuser
```

### 4. Start the development server
```bash
python manage.py runserver
```

### 5. Access the admin interface
Open browser: `http://127.0.0.1:8000/admin/`

## 📝 Usage Examples

### Example 1: Creating a Message (Triggers Notification)

```python
from django.contrib.auth.models import User
from messaging.models import Message, Notification

# Get or create users
alice = User.objects.create_user(username='alice', password='pass123')
bob = User.objects.create_user(username='bob', password='pass123')

# Send a message from alice to bob
message = Message.objects.create(
    sender=alice,
    receiver=bob,
    content="Hey Bob, how are you doing?"
)

# Notification is AUTOMATICALLY created for bob!
# Check bob's notifications
bob_notifications = Notification.objects.filter(user=bob)
print(f"Bob has {bob_notifications.count()} unread notifications")

# Output: ✅ Notification created for bob: New message from alice
# Output: Bob has 1 unread notifications
```

### Example 2: Checking Notifications

```python
# Get all unread notifications for bob
unread = Notification.objects.filter(user=bob, is_read=False)

for notification in unread:
    print(f"New message from: {notification.message.sender.username}")
    print(f"Content: {notification.message.content}")
    print(f"Received at: {notification.created_at}")
    
    # Mark as read
    notification.mark_as_read()
```

### Example 3: Multiple Messages

```python
# Alice sends 3 messages to Bob
for i in range(3):
    Message.objects.create(
        sender=alice,
        receiver=bob,
        content=f"Message number {i+1}"
    )

# Bob automatically has 3 new notifications!
print(f"Bob has {Notification.objects.filter(user=bob).count()} notifications")
# Output: Bob has 3 notifications
```

## 🧪 Running Tests

Run all tests:
```bash
python manage.py test messaging
```

Run specific test class:
```bash
python manage.py test messaging.tests.NotificationSignalTest
```

Run with verbose output:
```bash
python manage.py test messaging --verbosity=2
```

### Test Results
```
Found 9 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.........
----------------------------------------------------------------------
Ran 9 tests in 4.074s

OK
```

All 9 tests pass successfully! ✅

## 📁 Project Structure

```
Django-signals_orm-0x04/
├── messaging/
│   ├── __init__.py
│   ├── admin.py          # Admin interface configuration
│   ├── apps.py           # App configuration (registers signals)
│   ├── models.py         # Message and Notification models
│   ├── signals.py        # Signal handlers for auto-notifications
│   ├── tests.py          # Comprehensive test suite
│   ├── migrations/
│   │   └── 0001_initial.py
│   └── ...
├── messaging_project/
│   ├── settings.py       # Project settings
│   └── ...
├── manage.py
├── db.sqlite3
└── README.md
```

## 🔑 Key Concepts

### What are Signals?

Signals allow **decoupled applications** to get notified when actions occur elsewhere in the codebase.

**Benefits:**
- ✅ **Separation of Concerns**: Notification logic separate from message creation
- ✅ **Reusability**: Signal works anywhere messages are created
- ✅ **Maintainability**: Easy to add/remove without changing core code
- ✅ **Automatic**: No need to remember to create notifications manually

### Signal Components:

1. **Signal**: `post_save` - Triggered after a model instance is saved
2. **Sender**: `Message` model - What triggers the signal
3. **Receiver**: `create_notification_on_message()` - Function that handles the signal
4. **Decorator**: `@receiver` - Connects receiver to signal

### Why post_save?

- Fires **after** the model instance is saved to the database
- Guarantees the Message exists before creating Notification
- Can check `created` parameter to distinguish new vs updated instances

## 🎓 Learning Outcomes

After completing this project, you understand:

1. ✅ How to define Django models with relationships
2. ✅ How to use Django signals for event-driven programming
3. ✅ How to register signals in app configuration
4. ✅ How to write comprehensive tests for signals
5. ✅ How to create admin interfaces for model management
6. ✅ Best practices for decoupled Django applications

## 🐛 Troubleshooting

### Signals not working?

**Check:**
1. Is `messaging.apps.MessagingConfig` in `INSTALLED_APPS`?
2. Does `MessagingConfig.ready()` import `messaging.signals`?
3. Is the `@receiver` decorator used correctly?

### Duplicate notifications?

**Check:**
- Signal handler should check `if created:` to avoid duplicates on updates

### Tests failing?

**Check:**
```bash
python manage.py check  # Check for configuration errors
python manage.py migrate  # Ensure migrations are applied
```

## 📊 Admin Interface Features

### Message Admin
- View all messages
- Filter by sender, receiver, timestamp
- Search by username or content
- See content preview (first 50 characters)

### Notification Admin
- View all notifications
- Filter by read/unread status
- Mark multiple notifications as read/unread
- See message sender directly
- Sort by creation time

## 🔄 Signal Flow Diagram

```
Message Created
      ↓
post_save signal
      ↓
Signal dispatcher
      ↓
@receiver decorator identifies handler
      ↓
create_notification_on_message()
      ↓
Check if created == True
      ↓
Notification.objects.create()
      ↓
Notification saved to database
```

## 📈 Performance Considerations

- Signals execute synchronously (blocking)
- For high-volume apps, consider:
  - Celery for async notifications
  - Bulk create for multiple notifications
  - Database indexing on frequently queried fields

## 🎯 Extension Ideas

1. **Email Notifications**: Send email when notification is created
2. **Push Notifications**: Integrate with Firebase/OneSignal
3. **Real-time Updates**: Use Django Channels for WebSocket notifications
4. **Notification Preferences**: Let users choose notification types
5. **Read Receipts**: Track when messages are read

## 📚 Files Delivered

- ✅ `messaging/models.py` - Message and Notification models
- ✅ `messaging/signals.py` - Signal handler for auto-notifications
- ✅ `messaging/apps.py` - App config with signal registration
- ✅ `messaging/admin.py` - Admin interface configuration
- ✅ `messaging/tests.py` - Comprehensive test suite (9 tests)

## 🎉 Success Metrics

- ✅ Models created successfully
- ✅ Migrations applied without errors
- ✅ Signals registered and working
- ✅ All 9 tests passing
- ✅ Admin interface functional
- ✅ Automatic notification creation verified

## 📖 Additional Resources

- [Django Signals Documentation](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Django Model Relationships](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)

---

**Repository**: alx-backend-python  
**Directory**: Django-signals_orm-0x04  
**Status**: ✅ Complete and tested  
**Date**: November 29, 2025
