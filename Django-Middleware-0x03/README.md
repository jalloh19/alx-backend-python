# Django Middleware Project - 0x03

This project implements custom middleware for a Django messaging application with various security and monitoring features.

## Project Structure

```
Django-Middleware-0x03/
├── chats/
│   ├── middleware.py          # Custom middleware classes
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── ...
├── messaging_app/
│   ├── settings.py            # Middleware configuration
│   └── ...
└── requests.log               # Request logging file
```

## Implemented Middleware

### 1. RequestLoggingMiddleware
**Purpose**: Logs each user's requests to a file with timestamp, user, and request path.

**Location**: `chats/middleware.py`

**Output**: Logs are written to `requests.log`

**Example log entry**:
```
2025-11-29 10:30:45.123456 - User: alice - Path: /api/conversations/
2025-11-29 10:31:12.654321 - User: Anonymous - Path: /api/token/
```

---

### 2. RestrictAccessByTimeMiddleware
**Purpose**: Restricts access to the messaging app outside of business hours (9 AM to 6 PM).

**Behavior**:
- ✅ Allows access between 9:00 AM and 6:00 PM
- ❌ Returns `403 Forbidden` outside these hours

**Response example** (outside allowed hours):
```json
{
  "error": "Access forbidden",
  "message": "Chat access is restricted outside of 9 AM to 6 PM",
  "current_time": "20:45:30"
}
```

---

### 3. OffensiveLanguageMiddleware (Rate Limiting)
**Purpose**: Limits the number of chat messages a user can send based on their IP address.

**Configuration**:
- **Rate limit**: 5 messages per minute
- **Tracking**: Based on IP address
- **Applies to**: POST requests only

**Behavior**:
- Tracks POST requests from each IP
- Blocks further messages if limit exceeded
- Returns `429 Too Many Requests`

**Response example** (when limit exceeded):
```json
{
  "error": "Rate limit exceeded",
  "message": "You can only send 5 messages per minute",
  "retry_after": "60 seconds"
}
```

---

### 4. RolePermissionMiddleware
**Purpose**: Enforces role-based access control for specific endpoints.

**Configuration**:
- **Allowed roles**: `admin`, `moderator`
- **Protected paths**: `/api/conversations/`, `/api/messages/`

**Behavior**:
- Checks if user is authenticated
- Verifies user role before granting access
- Returns `403 Forbidden` for unauthorized roles

**Response example** (insufficient permissions):
```json
{
  "error": "Permission denied",
  "message": "Only admin and moderator users can access this resource",
  "your_role": "guest"
}
```

---

## Setup Instructions

### 1. Navigate to the project directory
```bash
cd Django-Middleware-0x03
```

### 2. Apply migrations
```bash
python manage.py migrate
```

### 3. Create users with different roles
```bash
python manage.py shell
```

Then run:
```python
from chats.models import User

# Create admin user
admin = User.objects.create_user(
    username='admin',
    password='admin123',
    email='admin@example.com',
    first_name='Admin',
    last_name='User',
    role='admin'
)

# Create moderator user
moderator = User.objects.create_user(
    username='moderator',
    password='mod123',
    email='mod@example.com',
    first_name='Moderator',
    last_name='User',
    role='moderator'
)

# Create regular user (guest)
guest = User.objects.create_user(
    username='guest',
    password='guest123',
    email='guest@example.com',
    first_name='Guest',
    last_name='User',
    role='guest'
)

print("Users created successfully!")
```

### 4. Start the development server
```bash
python manage.py runserver
```

---

## Testing the Middleware

### Test 1: Request Logging
**What it does**: Every request is logged to `requests.log`

**Test steps**:
1. Start the server
2. Make any API request
3. Check the `requests.log` file:
   ```bash
   tail -f requests.log
   ```

**Expected result**: You should see log entries with timestamp, user, and path.

---

### Test 2: Time-Based Access Restriction
**What it does**: Blocks access outside 9 AM - 6 PM

**Test steps**:
1. If testing outside business hours, access any endpoint
2. You should receive a 403 Forbidden response

**To test during development** (bypass for testing):
```python
# Temporarily comment out in settings.py
# "chats.middleware.RestrictAccessByTimeMiddleware",
```

---

### Test 3: Rate Limiting
**What it does**: Limits POST requests to 5 per minute per IP

**Test steps**:
1. Login to get JWT token:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

2. Send 6 POST requests rapidly:
   ```bash
   # Replace YOUR_TOKEN with actual token
   for i in {1..6}; do
     curl -X POST http://127.0.0.1:8000/api/messages/ \
       -H "Authorization: Bearer YOUR_TOKEN" \
       -H "Content-Type: application/json" \
       -d '{"conversation": "CONVERSATION_ID", "message_body": "Test '$i'"}'
     echo "\nRequest $i sent"
   done
   ```

**Expected result**: First 5 succeed, 6th returns `429 Too Many Requests`.

---

### Test 4: Role-Based Permissions
**What it does**: Only admin/moderator can access protected endpoints

**Test steps**:

1. Login as guest user:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "guest", "password": "guest123"}'
   ```

2. Try to access conversations:
   ```bash
   curl -X GET http://127.0.0.1:8000/api/conversations/ \
     -H "Authorization: Bearer GUEST_TOKEN"
   ```

**Expected result**: `403 Forbidden` with message about role permissions.

3. Login as admin:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

4. Try to access conversations:
   ```bash
   curl -X GET http://127.0.0.1:8000/api/conversations/ \
     -H "Authorization: Bearer ADMIN_TOKEN"
   ```

**Expected result**: Success! Conversations returned.

---

## Middleware Configuration in settings.py

The middleware is configured in `messaging_app/settings.py`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom middleware
    "chats.middleware.RequestLoggingMiddleware",
    "chats.middleware.RestrictAccessByTimeMiddleware",
    "chats.middleware.OffensiveLanguageMiddleware",
    "chats.middleware.RolePermissionMiddleware",
]
```

**Order matters!** Middleware is executed:
- Top to bottom for requests
- Bottom to top for responses

---

## Middleware Execution Flow

```
Request →
  │
  ├─ RequestLoggingMiddleware (logs request)
  ├─ RestrictAccessByTimeMiddleware (checks time)
  ├─ OffensiveLanguageMiddleware (checks rate limit)
  ├─ RolePermissionMiddleware (checks permissions)
  │
  └─→ View Handler
       │
       ← Response
```

---

## Troubleshooting

### Issue: Middleware not working
**Solution**: Ensure middleware is added to `MIDDLEWARE` in settings.py

### Issue: Role check always failing
**Solution**: Verify users have `role` attribute set (admin, moderator, guest, host)

### Issue: Rate limiting not working
**Solution**: Rate limits are per IP address. Testing from the same machine will trigger limits.

### Issue: Time restriction always blocks
**Solution**: Check server time matches your timezone. Adjust times in middleware if needed.

### Issue: Logs not being written
**Solution**: Ensure write permissions for `requests.log` file

---

## Files Delivered

✅ `chats/middleware.py` - All four middleware classes
✅ `requests.log` - Log file for request logging
✅ `messaging_app/settings.py` - Updated with middleware configuration
✅ `README.md` - This documentation

---

## Repository Information

- **GitHub repository**: alx-backend-python
- **Directory**: Django-Middleware-0x03
- **Files**: All files in Django-Middleware-0x03/*

---

## Key Features

1. ✅ **Request Logging**: All requests logged with timestamp and user info
2. ✅ **Time-Based Access Control**: Restricts access to business hours
3. ✅ **Rate Limiting**: Prevents spam (5 messages/minute per IP)
4. ✅ **Role-Based Permissions**: Admin/moderator only access
5. ✅ **Security**: Multiple layers of protection

---

## Next Steps

1. Test each middleware individually
2. Review logs in `requests.log`
3. Adjust middleware parameters as needed
4. Deploy to production with appropriate settings

---

**Author**: ALX Backend Python Project
**Date**: November 29, 2025
