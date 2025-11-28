# Messaging App API - Postman Testing Guide

## Overview
This directory contains Postman collections for testing the Messaging App API endpoints including authentication, conversations, and messages.

## Setup Instructions

### 1. Install Postman
- Download and install Postman from https://www.postman.com/downloads/

### 2. Import the Collection
1. Open Postman
2. Click "Import" button (top left)
3. Select `Messaging_App_API_Tests.postman_collection.json`
4. The collection will be imported with all test cases

### 3. Configure Environment Variables
The collection uses these environment variables:
- `base_url`: http://127.0.0.1:8000 (default)
- `access_token`: Auto-set after login
- `refresh_token`: Auto-set after login
- `conversation_id`: Auto-set after creating conversation
- `message_id`: Auto-set after sending message

To set the base_url manually:
1. Click on "Environments" in left sidebar
2. Create new environment (e.g., "Local Development")
3. Add variable: `base_url` = `http://127.0.0.1:8000`
4. Select this environment from dropdown (top right)

### 4. Start the Django Server
```bash
cd messaging_app
python manage.py runserver
```

### 5. Create Test Users
Before running the tests, create test users using Django admin or shell:

```bash
python manage.py createsuperuser
# Or
python manage.py shell
```

In Django shell:
```python
from chats.models import User
user1 = User.objects.create_user(
    username='testuser1',
    password='testpass123',
    email='testuser1@example.com',
    first_name='Test',
    last_name='User1',
    role='guest'
)
user2 = User.objects.create_user(
    username='testuser2',
    password='testpass123',
    email='testuser2@example.com',
    first_name='Test',
    last_name='User2',
    role='guest'
)
```

## Test Execution Order

### Phase 1: Authentication Tests
Run these tests first to obtain JWT tokens:

1. **Obtain JWT Token**
   - Tests user login
   - Saves access_token and refresh_token to environment
   - Expected: 200 OK with tokens

2. **Verify JWT Token**
   - Validates the access token
   - Expected: 200 OK

3. **Refresh JWT Token**
   - Tests token refresh functionality
   - Expected: 200 OK with new access token

4. **Unauthorized Access Test**
   - Tests that unauthenticated requests are rejected
   - Expected: 401 Unauthorized

### Phase 2: Conversation Tests
After authentication, test conversation endpoints:

5. **Create Conversation**
   - Creates a new conversation
   - Saves conversation_id to environment
   - Expected: 201 Created

6. **List All Conversations**
   - Fetches all conversations for authenticated user
   - Tests pagination structure
   - Expected: 200 OK with paginated results

7. **Get Conversation by ID**
   - Retrieves specific conversation
   - Expected: 200 OK with conversation details

8. **Filter Conversations by Participant**
   - Tests filtering functionality
   - Expected: 200 OK with filtered results

### Phase 3: Message Tests
Test messaging functionality:

9. **Send Message to Conversation**
   - Sends a message to existing conversation
   - Saves message_id to environment
   - Expected: 201 Created

10. **List All Messages (Paginated)**
    - Fetches messages with 20 per page
    - Tests pagination (count, next, previous, results)
    - Expected: 200 OK with max 20 messages per page

11. **Get Messages by Conversation**
    - Filters messages by conversation
    - Expected: 200 OK with conversation messages

12. **Filter Messages by Time Range**
    - Tests date filtering
    - Expected: 200 OK with filtered messages

13. **Filter Messages by Sender**
    - Tests sender filtering
    - Expected: 200 OK with filtered messages

14. **Get Message by ID**
    - Retrieves specific message
    - Expected: 200 OK

15. **Unauthorized Message Access Test**
    - Tests that non-participants cannot send messages
    - Expected: 403 Forbidden

## Running All Tests

### Option 1: Run Collection with Runner
1. Click on collection name
2. Click "Run" button
3. Select all requests
4. Click "Run Messaging App API Tests"
5. View test results

### Option 2: Run Individual Tests
1. Expand collection folders
2. Click on individual requests
3. Click "Send" button
4. View response and test results in "Test Results" tab

## Test Assertions

Each request includes automated test scripts that verify:
- **Status codes** (200, 201, 401, 403, 404)
- **Response structure** (JSON format, required fields)
- **Pagination** (count, next, previous, results)
- **Authentication** (token validity)
- **Authorization** (participant-only access)
- **Data integrity** (IDs, relationships)

## Common Test Scenarios

### Scenario 1: Complete User Flow
1. Obtain JWT Token (login)
2. Create Conversation
3. Send Message to Conversation
4. List All Messages
5. Get Messages by Conversation

### Scenario 2: Authentication & Authorization
1. Unauthorized Access Test (no token) → 401
2. Obtain JWT Token
3. Verify JWT Token → 200
4. Unauthorized Message Access Test (wrong conversation) → 403

### Scenario 3: Pagination & Filtering
1. List All Messages (page 1)
2. List All Messages (page 2)
3. Filter Messages by Time Range
4. Filter Messages by Sender
5. Filter Conversations by Participant

## Troubleshooting

### Issue: 401 Unauthorized
- Ensure you've run "Obtain JWT Token" first
- Check that access_token is saved in environment
- Token might be expired - run "Refresh JWT Token"

### Issue: 403 Forbidden
- User is not a participant in the conversation
- Check conversation_id is correct
- Verify user has proper permissions

### Issue: 404 Not Found
- conversation_id or message_id might be invalid
- Check that resources were created successfully
- Verify UUIDs are correct

### Issue: Connection Refused
- Ensure Django server is running: `python manage.py runserver`
- Check base_url is correct: http://127.0.0.1:8000
- Verify port 8000 is not blocked

## Expected Test Results

### Success Metrics
- **Authentication**: All 5 tests passing
- **Conversations**: All 4 tests passing
- **Messages**: All 7 tests passing
- **Total**: 16/16 tests passing

### Response Times
- Authentication: < 500ms
- Conversations: < 300ms
- Messages: < 400ms

## Additional Notes

### JWT Token Lifecycle
- Access tokens expire after 60 minutes
- Refresh tokens expire after 7 days
- Use "Refresh JWT Token" to get new access token

### Pagination
- Default page size: 20 messages
- Maximum page size: 100
- Use `?page=2` for next page
- Use `?page_size=10` for custom size

### Filtering Examples
- By time: `?sent_after=2025-11-01&sent_before=2025-12-01`
- By sender: `?sender_username=testuser1`
- By conversation: `?conversation={{conversation_id}}`
- Combined: `?sender_username=test&sent_after=2025-11-01`

## Support
For issues or questions, refer to the main project README or API documentation.
