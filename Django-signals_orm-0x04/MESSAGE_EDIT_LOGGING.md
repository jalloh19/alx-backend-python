# Message Edit Logging System

This implementation provides a complete signal-based system for logging message edits in Django.

## Features Implemented

### 1. **Message Model Enhancement**
- Added `edited` field (BooleanField) to track if a message has been edited
- Automatically set to `True` when content is modified

### 2. **MessageHistory Model**
A new model to store edit history with the following fields:
- `message`: ForeignKey to the edited Message
- `old_content`: TextField storing the previous content
- `edited_at`: DateTimeField recording when the edit occurred
- `edited_by`: ForeignKey to User who made the edit

### 3. **Pre-Save Signal**
Implemented `log_message_edit` signal handler that:
- Triggers before a Message is saved (using `pre_save` signal)
- Checks if the message already exists in the database
- Compares old and new content
- Creates a MessageHistory record if content has changed
- Marks the message as edited

### 4. **Admin Interface**
Enhanced Django admin with:
- **MessageAdmin**: Added `edited` field to list display
- **MessageHistoryAdmin**: 
  - Read-only access to history records
  - Prevents manual creation (only via signals)
  - Shows message ID, sender, old content preview, editor, and timestamp
  - Search and filter capabilities

### 5. **User Interface Views**
Created three views:
- **user_messages**: Display all sent and received messages with edit indicators
- **message_history**: Show complete edit history for a specific message
- **message_history_json**: API endpoint returning history as JSON

### 6. **Templates**
- `user_messages.html`: Lists all user messages with edit badges and history links
- `message_history.html`: Displays message details with chronological edit history

## File Structure

```
messaging/
├── models.py              # Message, MessageHistory, Notification models
├── signals.py             # Signal handlers for notifications and edit logging
├── admin.py               # Admin configurations
├── views.py               # Views for message history
├── urls.py                # URL patterns for messaging app
├── templates/
│   └── messaging/
│       ├── message_history.html
│       └── user_messages.html
└── migrations/
    └── 0002_message_edited_messagehistory.py
```

## How It Works

### Signal Flow
1. User edits a message and saves it
2. `pre_save` signal is triggered BEFORE saving to database
3. Signal handler retrieves the old message from database
4. Compares old content with new content
5. If different, creates MessageHistory record with old content
6. Sets `message.edited = True`
7. Message is saved with updated content

### Data Flow Example
```python
# Initial message
message = Message.objects.create(
    sender=user1,
    receiver=user2,
    content="Hello, how are you?"
)

# First edit
message.content = "Hello, how are you doing?"
message.save()
# → MessageHistory created with "Hello, how are you?"
# → message.edited = True

# Second edit
message.content = "Hello, how are you doing today?"
message.save()
# → MessageHistory created with "Hello, how are you doing?"
# → message.edited remains True
```

## Usage

### Viewing Message History in Admin
1. Navigate to Django admin panel
2. Go to "Message Histories" section
3. View all edit records with timestamps and old content

### Viewing History in User Interface
1. Access `/messages/` to see all your messages
2. Edited messages show an "EDITED" badge
3. Click "View Edit History" link to see all previous versions
4. Each edit shows the old content and timestamp

### API Access
Get message history as JSON:
```bash
GET /message/<message_id>/history/json/
```

Response:
```json
{
    "message_id": 1,
    "current_content": "Latest content",
    "edited": true,
    "history": [
        {
            "id": 1,
            "old_content": "Previous content",
            "edited_at": "2025-11-29T10:30:00Z",
            "edited_by": "username"
        }
    ]
}
```

## Security Considerations
- Only message sender and receiver can view edit history
- MessageHistory records cannot be manually created in admin
- History records are preserved even if message is deleted (can be modified)

## Testing the Implementation

### Via Django Shell
```python
from django.contrib.auth.models import User
from messaging.models import Message, MessageHistory

# Create users
user1 = User.objects.create_user('alice', password='pass')
user2 = User.objects.create_user('bob', password='pass')

# Create message
msg = Message.objects.create(
    sender=user1,
    receiver=user2,
    content="Original message"
)

# Edit message
msg.content = "Edited message"
msg.save()

# Check history
print(f"Message edited: {msg.edited}")  # True
print(f"History count: {msg.history.count()}")  # 1
print(f"Old content: {msg.history.first().old_content}")  # "Original message"
```

### Via Admin Panel
1. Create a message in admin
2. Edit the message content
3. View "Message Histories" to see the logged edit
4. Check that the message shows "edited: ✓"

## Key Points
- ✅ Uses `pre_save` signal for automatic logging
- ✅ Tracks edit history in separate model
- ✅ Provides both UI and API access
- ✅ Maintains data integrity
- ✅ User-friendly interface with visual indicators
- ✅ Complete audit trail of all changes
