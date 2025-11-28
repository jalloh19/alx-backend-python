# Quick Start Guide: Testing Your Messaging App API with Postman

## Step 1: Prepare Your Django Server

### 1.1 Start the server
```bash
cd messaging_app
python manage.py runserver
```

Keep this terminal running. You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### 1.2 Create a test user
Open a NEW terminal and run:
```bash
cd messaging_app
python manage.py shell
```

Then paste this code:
```python
from chats.models import User

# Create first test user
user1 = User.objects.create_user(
    username='alice',
    password='password123',
    email='alice@example.com',
    first_name='Alice',
    last_name='Smith',
    role='guest'
)

# Create second test user
user2 = User.objects.create_user(
    username='bob',
    password='password123',
    email='bob@example.com',
    first_name='Bob',
    last_name='Jones',
    role='guest'
)

print("Users created successfully!")
```

Press Ctrl+D to exit the shell.

## Step 2: Install and Setup Postman

### 2.1 Download Postman
- Go to https://www.postman.com/downloads/
- Download for your operating system
- Install and open Postman

### 2.2 Import the Collection
1. Click the **"Import"** button (top-left corner)
2. Click **"Upload Files"**
3. Navigate to: `messaging_app/post_man-Collections/`
4. Select: `Messaging_App_API_Tests.postman_collection.json`
5. Click **"Import"**

You'll see a new collection called **"Messaging App API Tests"** in your Collections sidebar.

## Step 3: Run Your First Test (Login)

### 3.1 Expand the Collection
- Click on **"Messaging App API Tests"** in the left sidebar
- Click on **"Authentication"** folder to expand it
- Click on **"Obtain JWT Token"**

### 3.2 Update the Login Credentials
In the request body, you'll see:
```json
{
  "username": "testuser1",
  "password": "testpass123"
}
```

Change it to match the user you created:
```json
{
  "username": "alice",
  "password": "password123"
}
```

### 3.3 Send the Request
1. Click the blue **"Send"** button
2. Look at the response at the bottom:
   - Status should be `200 OK` (green)
   - You'll see `access` and `refresh` tokens

**Success!** You just logged in and got your authentication tokens.

## Step 4: Create a Conversation

### 4.1 Open the Request
- Click on **"Conversations"** folder
- Click on **"Create Conversation"**

### 4.2 Send the Request
- Just click **"Send"** (no changes needed)
- Status should be `201 Created` (green)
- You'll see a `conversation_id` in the response

**Success!** You created your first conversation.

## Step 5: Send a Message

### 5.1 Open the Request
- Click on **"Messages"** folder
- Click on **"Send Message to Conversation"**

### 5.2 Check the Message Body
You'll see something like:
```json
{
  "conversation": "{{conversation_id}}",
  "message_body": "Hello! This is a test message."
}
```

The `{{conversation_id}}` is automatically filled from Step 4.

### 5.3 Send the Request
- Click **"Send"**
- Status should be `201 Created`
- You'll see your message with a `message_id`

**Success!** You sent your first message.

## Step 6: View Your Messages

### 6.1 List All Messages
- Click on **"List All Messages (Paginated)"**
- Click **"Send"**
- You'll see all your messages (max 20 per page)

### 6.2 View Messages in a Conversation
- Click on **"Get Messages by Conversation"**
- Click **"Send"**
- You'll see only messages from that specific conversation

## Understanding the Tests

### What Happens Automatically?

When you run tests, Postman automatically:
1. **Saves your login tokens** - No need to copy/paste
2. **Saves conversation IDs** - Uses them in later requests
3. **Saves message IDs** - For testing specific messages
4. **Runs test assertions** - Shows ✓ or ✗ for each test

### Where to See Test Results?

After clicking "Send", look at the bottom panel:
- **Body tab**: Shows the actual response data
- **Test Results tab**: Shows if tests passed (green ✓) or failed (red ✗)

Example:
```
✓ Status code is 200
✓ Access token is present
✓ Refresh token is present
```

## Common Scenarios

### Scenario 1: Full Message Flow
1. **Obtain JWT Token** (login as alice)
2. **Create Conversation**
3. **Send Message to Conversation**
4. **List All Messages**

Do these in order, clicking "Send" for each.

### Scenario 2: Test Unauthorized Access
1. **Unauthorized Access Test** (in Authentication folder)
   - This should FAIL with 401 (that's correct!)
   - It proves you can't access without login

2. **Obtain JWT Token** (login)

3. **Unauthorized Message Access Test** (in Messages folder)
   - This should FAIL with 403 (that's correct!)
   - It proves you can't send messages to conversations you're not in

### Scenario 3: Test Pagination
1. **Obtain JWT Token** (login)
2. **Send Message to Conversation** (repeat this 25 times)
3. **List All Messages (Paginated)**
   - Change the URL to add `?page=1`
   - You'll see first 20 messages
   - Change to `?page=2`
   - You'll see remaining 5 messages

## Visual Guide: What You'll See

### When Login Succeeds:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

### When Creating Conversation:
```json
{
  "conversation_id": "a1b2c3d4-...",
  "participants": [
    {
      "user_id": "...",
      "username": "alice",
      "email": "alice@example.com"
    }
  ],
  "messages": [],
  "created_at": "2025-11-29T..."
}
```

### When Sending Message:
```json
{
  "message_id": "e5f6g7h8-...",
  "sender": {
    "user_id": "...",
    "username": "alice"
  },
  "conversation": "a1b2c3d4-...",
  "message_body": "Hello! This is a test message.",
  "sent_at": "2025-11-29T..."
}
```

### When Listing Messages (Paginated):
```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/messages/?page=2",
  "previous": null,
  "results": [
    { "message_id": "...", "message_body": "..." },
    { "message_id": "...", "message_body": "..." }
    // ... 18 more messages (20 total)
  ]
}
```

## Troubleshooting

### Problem: "Could not get any response"
**Solution**: Make sure Django server is running
```bash
python manage.py runserver
```

### Problem: "401 Unauthorized"
**Solution**: Run "Obtain JWT Token" first to login

### Problem: "403 Forbidden"
**Solution**: You're trying to access a conversation you're not part of
- This is expected for the "Unauthorized Message Access Test"
- For other requests, make sure you created the conversation first

### Problem: "404 Not Found"
**Solution**: The conversation_id or message_id doesn't exist
- Make sure you ran "Create Conversation" first
- Check that the {{conversation_id}} variable is set

### Problem: Tests show "undefined" errors
**Solution**: Run tests in order:
1. Authentication tests first
2. Then Conversation tests
3. Finally Message tests

## Advanced: Running All Tests at Once

### Using Collection Runner
1. Click on **"Messaging App API Tests"** (the collection name)
2. Click the **"Run"** button (top right)
3. Check all the requests you want to run
4. Click **"Run Messaging App API Tests"**
5. Watch all tests execute automatically!

**Note**: Make sure to run in this order for best results:
- Authentication folder (all)
- Conversations folder (all)
- Messages folder (all)

## Next Steps

Once comfortable with basic tests:

### 1. Try Filtering
- **Filter by sender**: Change URL to `?sender_username=alice`
- **Filter by date**: Add `?sent_after=2025-11-01&sent_before=2025-12-01`

### 2. Test with Multiple Users
- Create conversations with bob
- Login as bob (change username in "Obtain JWT Token")
- Try to access alice's conversations (should fail with 403)

### 3. Test Pagination
- Send 25+ messages
- Use `?page=1`, `?page=2` to see pagination
- Verify max 20 messages per page

## Need Help?

- **Postman errors**: Check the console (View → Show Postman Console)
- **Django errors**: Check the terminal where `runserver` is running
- **Test failures**: Look at the "Test Results" tab for details

## Summary: Your Testing Workflow

```
1. Start Django server
   ↓
2. Create test users
   ↓
3. Open Postman and import collection
   ↓
4. Login (Obtain JWT Token)
   ↓
5. Create Conversation
   ↓
6. Send Messages
   ↓
7. View Messages (with filters/pagination)
   ↓
8. Test unauthorized access scenarios
```

**Happy Testing!** 🚀
