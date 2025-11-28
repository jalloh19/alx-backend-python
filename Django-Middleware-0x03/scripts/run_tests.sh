#!/bin/bash
# Automated test script for local development

set -e  # Exit on error

echo "🚀 Starting automated API testing workflow..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Apply migrations
echo -e "${BLUE}📦 Applying database migrations...${NC}"
cd /home/jalloh/Desktop/ALL/ALX_SE/alx-backend-python/messaging_app
python manage.py migrate

# Step 2: Create test users
echo -e "${BLUE}👥 Creating test users...${NC}"
python manage.py shell << EOF
from chats.models import User

# Delete existing test users if they exist
User.objects.filter(username__in=['alice', 'bob']).delete()

# Create fresh test users
user1 = User.objects.create_user(
    username='alice',
    password='password123',
    email='alice@example.com',
    first_name='Alice',
    last_name='Smith',
    role='guest'
)

user2 = User.objects.create_user(
    username='bob',
    password='password123',
    email='bob@example.com',
    first_name='Bob',
    last_name='Jones',
    role='host'
)

print("✅ Test users created: alice, bob")
EOF

# Step 3: Start Django server in background
echo -e "${BLUE}🌐 Starting Django server...${NC}"
python manage.py runserver 127.0.0.1:8000 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if curl -s http://127.0.0.1:8000/api/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running (PID: $SERVER_PID)${NC}"
else
    echo -e "${RED}❌ Server failed to start${NC}"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

# Step 4: Run Newman tests
echo -e "${BLUE}🧪 Running Postman tests with Newman...${NC}"
cd post_man-Collections

if command -v newman &> /dev/null; then
    newman run Messaging_App_API_Tests.postman_collection.json \
        -e local-environment.json \
        --reporters cli,htmlextra \
        --reporter-htmlextra-export ../test-reports/newman-report-$(date +%Y%m%d-%H%M%S).html \
        --color on
    
    TEST_EXIT_CODE=$?
else
    echo -e "${RED}❌ Newman not installed. Install with: npm install -g newman newman-reporter-htmlextra${NC}"
    TEST_EXIT_CODE=1
fi

# Step 5: Cleanup
echo -e "${BLUE}🧹 Stopping server...${NC}"
kill $SERVER_PID 2>/dev/null || true

# Step 6: Report results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo -e "${GREEN}📊 View detailed report in: messaging_app/test-reports/${NC}"
else
    echo -e "${RED}❌ Some tests failed. Check the output above.${NC}"
fi

exit $TEST_EXIT_CODE
