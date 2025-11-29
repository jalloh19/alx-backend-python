# Models.py Changes - Visual Summary

## Changes Made to Message Model

### BEFORE
```python
class Message(models.Model):
    sender = models.ForeignKey(User, ...)
    receiver = models.ForeignKey(User, ...)
    content = models.TextField(...)
    timestamp = models.DateTimeField(auto_now_add=True, ...)
    # No edited field
```

### AFTER
```python
class Message(models.Model):
    sender = models.ForeignKey(User, ...)
    receiver = models.ForeignKey(User, ...)
    content = models.TextField(...)
    timestamp = models.DateTimeField(auto_now_add=True, ...)
    edited = models.BooleanField(              # ← NEW FIELD
        default=False,
        help_text="Whether the message has been edited"
    )
```

## New Model Added: MessageHistory

```python
class MessageHistory(models.Model):
    """
    MessageHistory model for storing previous versions of edited messages.
    
    Automatically created via pre_save signal when a message is edited.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="The message that was edited"
    )
    old_content = models.TextField(
        help_text="The content before the edit"
    )
    edited_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the edit occurred"
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='message_edits',
        help_text="User who made the edit"
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name = 'Message History'
        verbose_name_plural = 'Message Histories'
        indexes = [
            models.Index(fields=['message', '-edited_at']),
        ]
```

## Database Schema

### Messages Table (Updated)
```
+------------+------------------+
| Field      | Type             |
+------------+------------------+
| id         | BigAutoField     |
| sender_id  | ForeignKey       |
| receiver_id| ForeignKey       |
| content    | TextField        |
| timestamp  | DateTimeField    |
| edited     | BooleanField ✨  | ← NEW
+------------+------------------+
```

### MessageHistory Table (New)
```
+------------+------------------+
| Field      | Type             |
+------------+------------------+
| id         | BigAutoField     |
| message_id | ForeignKey       |
| old_content| TextField        |
| edited_at  | DateTimeField    |
| edited_by_id| ForeignKey      |
+------------+------------------+
```

## Relationships

```
User ──┐
       ├─→ Message (sender)
       │   ├── edited: bool
       │   └── history ←──┐
       │                  │
       └─→ Message (receiver)
                          │
User ──────────────────────┼─→ MessageHistory
                          │    ├── old_content
                          │    ├── edited_at
                          └────┤   └── edited_by
                               │
                         [Many-to-One]
```

## Usage Examples

### Creating a Message
```python
message = Message.objects.create(
    sender=user1,
    receiver=user2,
    content="Hello!"
)
# edited = False (default)
# history.count() = 0
```

### Editing a Message (Triggers Signal)
```python
message.content = "Hello, how are you?"
message.save()

# AUTO-MAGIC via pre_save signal:
# 1. MessageHistory created with old content "Hello!"
# 2. message.edited set to True
# 3. Message saved with new content

# Results:
# message.edited = True
# message.history.count() = 1
```

### Accessing History
```python
# Get all history entries
for entry in message.history.all():
    print(f"Old: {entry.old_content}")
    print(f"When: {entry.edited_at}")
    print(f"By: {entry.edited_by.username}")

# Get latest edit
latest = message.history.first()
print(f"Previous content: {latest.old_content}")

# Count edits
edit_count = message.history.count()
print(f"This message was edited {edit_count} times")
```

## Files Modified/Created

```
messaging/
├── models.py          ← MODIFIED (added edited field + MessageHistory model)
├── signals.py         ← MODIFIED (added pre_save signal handler)
├── admin.py           ← MODIFIED (added MessageHistoryAdmin)
├── views.py           ← MODIFIED (added history views)
├── urls.py            ← CREATED
└── templates/         ← CREATED
    └── messaging/
        ├── message_history.html
        └── user_messages.html
```

## Migration Details

**File**: `messaging/migrations/0002_message_edited_messagehistory.py`

**Operations**:
1. `AddField` - adds `edited` field to Message model
2. `CreateModel` - creates MessageHistory model with all fields

**Applied**: ✅ Successfully migrated to database

## Key Features

✅ **Automatic Logging**: No manual code needed, signal handles everything
✅ **Complete History**: Every edit is tracked chronologically  
✅ **User Attribution**: Tracks who made each edit
✅ **Data Integrity**: Old content preserved, never lost
✅ **Efficient Queries**: Indexed for fast lookups
✅ **Related Access**: `message.history.all()` gives all edits
✅ **Smart Detection**: Only logs when content actually changes
✅ **Edit Flag**: `message.edited` quickly shows if modified

## File Location

**Repository**: alx-backend-python  
**Directory**: Django-signals_orm-0x04  
**Primary File**: messaging/models.py  

✅ All changes committed and tested successfully!
