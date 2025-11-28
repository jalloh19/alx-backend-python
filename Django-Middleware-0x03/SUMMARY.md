# Django Middleware Project - Quick Reference

## ✅ Project Setup Complete

All required files have been created and configured successfully!

## 📁 Deliverables Checklist

### Task 0: Project Setup ✅
- [x] Copied `messaging_app` directory to `Django-Middleware-0x03`
- [x] All files in `Django-Middleware-0x03/*` directory

### Task 1: Request Logging Middleware ✅
- [x] Created `chats/middleware.py`
- [x] Implemented `RequestLoggingMiddleware` class with `__init__` and `__call__`
- [x] Logs format: `{datetime.now()} - User: {user} - Path: {request.path}`
- [x] Created `requests.log` file
- [x] Configured in `settings.py`

### Task 2: Time-Based Access Restriction ✅
- [x] Implemented `RestrictAccessByTimeMiddleware` with `__init__` and `__call__`
- [x] Restricts access outside 9 AM - 6 PM
- [x] Returns `403 Forbidden` error
- [x] Configured in `settings.py`

### Task 3: Rate Limiting (Offensive Language Detection) ✅
- [x] Implemented `OffensiveLanguageMiddleware` with `__init__` and `__call__`
- [x] Tracks POST requests by IP address
- [x] Limits to 5 messages per minute
- [x] Returns `429 Too Many Requests` when limit exceeded
- [x] Configured in `settings.py`

### Task 4: Role Permission Middleware ✅
- [x] Implemented `RolePermissionMiddleware` with `__init__` and `__call__`
- [x] Checks user role (admin/moderator required)
- [x] Returns `403 Forbidden` for unauthorized roles
- [x] Configured in `settings.py`

## 🚀 Quick Start Commands

```bash
# Navigate to project
cd Django-Middleware-0x03

# Run verification tests
bash test_middleware.sh

# Apply migrations
python manage.py migrate

# Create test users
python manage.py shell < scripts/create_test_users.py

# Start server
python manage.py runserver
```

## 🧪 Testing Each Middleware

### 1. Test Request Logging
```bash
# Start server
python manage.py runserver

# Make any request, then check logs
tail -f requests.log
```

### 2. Test Time Restriction
```bash
# Access any endpoint outside 9 AM - 6 PM
curl http://127.0.0.1:8000/api/conversations/

# Expected: 403 Forbidden with time restriction message
```

### 3. Test Rate Limiting
```bash
# Send 6 POST requests rapidly (5 should succeed, 6th should fail)
# First get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r .access)

# Send multiple requests
for i in {1..6}; do
  curl -X POST http://127.0.0.1:8000/api/messages/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"message":"Test '$i'"}'
  echo ""
done
```

### 4. Test Role Permissions
```bash
# Login as guest user
GUEST_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"guest","password":"guest123"}' \
  | jq -r .access)

# Try to access protected endpoint (should fail)
curl -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $GUEST_TOKEN"

# Login as admin
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r .access)

# Try to access protected endpoint (should succeed)
curl -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## 📝 Implementation Details

### Middleware Classes Location
**File**: `Django-Middleware-0x03/chats/middleware.py`

Contains:
1. `RequestLoggingMiddleware` - Logs all requests
2. `RestrictAccessByTimeMiddleware` - Time-based access control
3. `OffensiveLanguageMiddleware` - Rate limiting by IP
4. `RolePermissionMiddleware` - Role-based access control

### Configuration Location
**File**: `Django-Middleware-0x03/messaging_app/settings.py`

```python
MIDDLEWARE = [
    # ... Django default middleware ...
    "chats.middleware.RequestLoggingMiddleware",
    "chats.middleware.RestrictAccessByTimeMiddleware",
    "chats.middleware.OffensiveLanguageMiddleware",
    "chats.middleware.RolePermissionMiddleware",
]
```

## 📊 Middleware Execution Order

Requests flow through middleware in this order:
1. **RequestLoggingMiddleware** → Logs the request
2. **RestrictAccessByTimeMiddleware** → Checks if within allowed hours
3. **OffensiveLanguageMiddleware** → Checks rate limits
4. **RolePermissionMiddleware** → Checks user permissions
5. **View Handler** → Processes the request

## 🎯 Key Features

| Middleware | Purpose | Status Code |
|------------|---------|-------------|
| RequestLoggingMiddleware | Log all requests | N/A (passes through) |
| RestrictAccessByTimeMiddleware | Time-based access (9AM-6PM) | 403 Forbidden |
| OffensiveLanguageMiddleware | Rate limiting (5/min) | 429 Too Many Requests |
| RolePermissionMiddleware | Role-based access | 403 Forbidden |

## 📂 Repository Information

- **GitHub repository**: `alx-backend-python`
- **Directory**: `Django-Middleware-0x03`
- **Files**: All files in `Django-Middleware-0x03/*`

## ✅ Verification

Run the automated test script:
```bash
cd Django-Middleware-0x03
bash test_middleware.sh
```

Expected output: All checks should pass ✅

## 📚 Additional Resources

- Full documentation: `README.md`
- Test script: `test_middleware.sh`
- Automation guide: `AUTOMATION_GUIDE.md`

## 🎉 Ready to Submit!

All tasks completed successfully. The project is ready for review.

---

**Generated**: November 29, 2025
**Project**: Django Middleware - 0x03
**Status**: ✅ Complete
