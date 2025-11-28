# Testing Guide for Django Middleware

This guide walks you through testing each middleware component.

## Prerequisites

1. Navigate to project directory:
```bash
cd /home/jalloh/Desktop/ALL/ALX_SE/alx-backend-python/Django-Middleware-0x03
```

2. Run verification:
```bash
bash test_middleware.sh
```

3. Apply migrations:
```bash
python manage.py migrate
```

4. Create test users:
```bash
python manage.py shell < scripts/create_test_users.py
```

## Test 1: RequestLoggingMiddleware

### Objective
Verify that all requests are logged to `requests.log` with timestamp, user, and path.

### Steps

1. **Start the server:**
```bash
python manage.py runserver
```

2. **In a new terminal, watch the log file:**
```bash
cd /home/jalloh/Desktop/ALL/ALX_SE/alx-backend-python/Django-Middleware-0x03
tail -f requests.log
```

3. **Make some requests:**
```bash
# Request as anonymous user
curl http://127.0.0.1:8000/api/

# Get JWT token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Request as authenticated user
curl http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

4. **Expected output in requests.log:**
```
2025-11-29 15:30:45.123456 - User: Anonymous - Path: /api/
2025-11-29 15:30:50.654321 - User: Anonymous - Path: /api/token/
2025-11-29 15:31:00.789012 - User: admin - Path: /api/conversations/
```

### ✅ Success Criteria
- Log file contains timestamp
- Shows "Anonymous" for unauthenticated requests
- Shows username for authenticated requests
- Logs the request path

---

## Test 2: RestrictAccessByTimeMiddleware

### Objective
Verify that access is restricted outside of 9 AM to 6 PM.

### Steps

1. **Check current server time:**
```bash
date +"%H:%M"
```

2. **If time is between 9 AM and 6 PM:**
```bash
# Should succeed
curl -X GET http://127.0.0.1:8000/api/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **If time is outside 9 AM - 6 PM:**
```bash
# Should return 403 Forbidden
curl -X GET http://127.0.0.1:8000/api/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Expected Response (Outside Hours)
```json
{
  "error": "Access forbidden",
  "message": "Chat access is restricted outside of 9 AM to 6 PM",
  "current_time": "20:30:45"
}
```

### 🧪 To Test During Development

**Option 1: Temporarily disable**
Comment out in `settings.py`:
```python
# "chats.middleware.RestrictAccessByTimeMiddleware",
```

**Option 2: Change time window**
Edit `chats/middleware.py`:
```python
# Change these lines to match current time
start_time = time(0, 0)   # Midnight
end_time = time(23, 59)   # 11:59 PM
```

### ✅ Success Criteria
- Returns 403 status code outside hours
- Shows appropriate error message
- Displays current server time
- Allows access within 9 AM - 6 PM

---

## Test 3: OffensiveLanguageMiddleware (Rate Limiting)

### Objective
Verify that POST requests are limited to 5 per minute per IP address.

### Steps

1. **Get authentication token:**
```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")
```

2. **Create a conversation first:**
```bash
CONV_ID=$(curl -s -X POST http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"participant_ids":["'$(python3 manage.py shell -c "from chats.models import User; print(User.objects.get(username='admin').user_id)")'"]}'
  | python3 -c "import sys, json; print(json.load(sys.stdin)['conversation_id'])")
```

3. **Send 6 POST requests rapidly:**
```bash
echo "Sending 6 messages (limit is 5 per minute)..."
for i in {1..6}; do
  echo "Request $i:"
  curl -X POST http://127.0.0.1:8000/api/messages/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"conversation\":\"$CONV_ID\",\"message_body\":\"Test message $i\"}"
  echo -e "\n"
  sleep 1
done
```

### Expected Behavior
- **Requests 1-5**: Success (201 Created)
- **Request 6**: Rate limit error (429 Too Many Requests)

### Expected Response (6th Request)
```json
{
  "error": "Rate limit exceeded",
  "message": "You can only send 5 messages per minute",
  "retry_after": "60 seconds"
}
```

### 🧪 Verify Rate Limit Reset
```bash
# Wait 60 seconds
sleep 60

# Try again (should succeed)
curl -X POST http://127.0.0.1:8000/api/messages/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"conversation\":\"$CONV_ID\",\"message_body\":\"Test after reset\"}"
```

### ✅ Success Criteria
- First 5 POST requests succeed
- 6th POST request returns 429 status
- Error message mentions rate limit
- After 60 seconds, requests work again

---

## Test 4: RolePermissionMiddleware

### Objective
Verify that only admin and moderator roles can access protected endpoints.

### Steps

1. **Test as GUEST (should fail):**
```bash
# Get guest token
GUEST_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"guest","password":"guest123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# Try to access conversations
echo "Testing as GUEST user:"
curl -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $GUEST_TOKEN"
echo -e "\n"
```

**Expected Response:**
```json
{
  "error": "Permission denied",
  "message": "Only admin and moderator users can access this resource",
  "your_role": "guest"
}
```

2. **Test as MODERATOR (should succeed):**
```bash
# Get moderator token
MOD_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"moderator","password":"mod123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# Try to access conversations
echo "Testing as MODERATOR user:"
curl -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $MOD_TOKEN"
echo -e "\n"
```

**Expected Response:** Success! List of conversations returned.

3. **Test as ADMIN (should succeed):**
```bash
# Get admin token
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# Try to access conversations
echo "Testing as ADMIN user:"
curl -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"
echo -e "\n"
```

**Expected Response:** Success! List of conversations returned.

4. **Test without authentication (should fail):**
```bash
# Try to access without token
echo "Testing without authentication:"
curl -X GET http://127.0.0.1:8000/api/conversations/
echo -e "\n"
```

**Expected Response:**
```json
{
  "error": "Authentication required",
  "message": "You must be logged in to access this resource"
}
```

### ✅ Success Criteria
- Guest users receive 403 Forbidden
- Admin users can access protected endpoints
- Moderator users can access protected endpoints
- Unauthenticated requests receive 401 Unauthorized
- Error messages clearly state the role requirement

---

## Complete Test Script

Run all tests automatically:

```bash
#!/bin/bash
# Complete middleware test script

echo "🧪 Running Complete Middleware Test Suite"
echo "=========================================="

# Start server in background
python manage.py runserver &
SERVER_PID=$!
sleep 3

# Test 1: Request Logging
echo -e "\n📝 Test 1: Request Logging"
curl -s http://127.0.0.1:8000/api/ > /dev/null
if grep -q "Anonymous" requests.log; then
    echo "✅ Request logging works"
else
    echo "❌ Request logging failed"
fi

# Test 2: Get tokens
echo -e "\n🔐 Getting authentication tokens..."
ADMIN_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

GUEST_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"guest","password":"guest123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

# Test 3: Role Permissions
echo -e "\n🔒 Test 4: Role Permissions"
GUEST_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $GUEST_TOKEN")

if [ "$GUEST_RESPONSE" = "403" ]; then
    echo "✅ Guest user correctly blocked"
else
    echo "❌ Guest user not blocked (got $GUEST_RESPONSE)"
fi

ADMIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X GET http://127.0.0.1:8000/api/conversations/ \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if [ "$ADMIN_RESPONSE" = "200" ]; then
    echo "✅ Admin user correctly allowed"
else
    echo "❌ Admin user not allowed (got $ADMIN_RESPONSE)"
fi

# Cleanup
echo -e "\n🧹 Cleaning up..."
kill $SERVER_PID
echo "✅ Test suite complete!"
```

Save as `test_all_middleware.sh` and run:
```bash
chmod +x test_all_middleware.sh
bash test_all_middleware.sh
```

---

## Troubleshooting

### Issue: Rate limiting not working
**Check:** Are you testing from the same IP? Rate limits are per IP address.
**Solution:** Wait 60 seconds between test runs.

### Issue: Role permissions always blocking
**Check:** Does the user have a role assigned?
```bash
python manage.py shell
from chats.models import User
user = User.objects.get(username='admin')
print(user.role)  # Should be 'admin'
```

### Issue: Time restriction not working
**Check:** Is the current time within 9 AM - 6 PM?
**Solution:** Adjust time window in middleware or test outside hours.

### Issue: Logs not appearing
**Check:** File permissions on `requests.log`
```bash
ls -la requests.log
chmod 666 requests.log  # If needed
```

---

## Summary

All middleware components work together to provide:
1. ✅ Request logging for monitoring
2. ✅ Time-based access control
3. ✅ Rate limiting to prevent abuse
4. ✅ Role-based permissions for security

**Next Steps:**
1. Run all tests
2. Review logs
3. Adjust configuration as needed
4. Deploy to production

---

**Last Updated**: November 29, 2025
