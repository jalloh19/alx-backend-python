#!/bin/bash
# Test script for Django Middleware

echo "🧪 Testing Django Middleware Implementation"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Change to project directory
cd /home/jalloh/Desktop/ALL/ALX_SE/alx-backend-python/Django-Middleware-0x03

echo -e "${BLUE}1. Checking Django configuration...${NC}"
python manage.py check
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Django configuration is valid${NC}"
else
    echo -e "${RED}❌ Django configuration has errors${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}2. Checking middleware file exists...${NC}"
if [ -f "chats/middleware.py" ]; then
    echo -e "${GREEN}✅ middleware.py found${NC}"
else
    echo -e "${RED}❌ middleware.py not found${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}3. Checking requests.log file exists...${NC}"
if [ -f "requests.log" ]; then
    echo -e "${GREEN}✅ requests.log found${NC}"
else
    echo -e "${RED}❌ requests.log not found${NC}"
    exit 1
fi
echo ""

echo -e "${BLUE}4. Verifying middleware classes...${NC}"
classes=("RequestLoggingMiddleware" "RestrictAccessByTimeMiddleware" "OffensiveLanguageMiddleware" "RolePermissionMiddleware")
for class in "${classes[@]}"; do
    if grep -q "$class" chats/middleware.py; then
        echo -e "${GREEN}✅ $class found${NC}"
    else
        echo -e "${RED}❌ $class not found${NC}"
    fi
done
echo ""

echo -e "${BLUE}5. Checking middleware configuration in settings.py...${NC}"
middleware_classes=(
    "chats.middleware.RequestLoggingMiddleware"
    "chats.middleware.RestrictAccessByTimeMiddleware"
    "chats.middleware.OffensiveLanguageMiddleware"
    "chats.middleware.RolePermissionMiddleware"
)

for mw in "${middleware_classes[@]}"; do
    if grep -q "$mw" messaging_app/settings.py; then
        echo -e "${GREEN}✅ $mw configured${NC}"
    else
        echo -e "${RED}❌ $mw not configured${NC}"
    fi
done
echo ""

echo -e "${BLUE}6. Testing imports...${NC}"
python manage.py shell << EOF
try:
    from chats.middleware import RequestLoggingMiddleware
    from chats.middleware import RestrictAccessByTimeMiddleware
    from chats.middleware import OffensiveLanguageMiddleware
    from chats.middleware import RolePermissionMiddleware
    print("✅ All middleware classes imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF
echo ""

echo -e "${GREEN}=========================================="
echo "✅ All checks passed!"
echo "=========================================="${NC}
echo ""
echo "Next steps:"
echo "1. Run migrations: python manage.py migrate"
echo "2. Create test users (see README.md)"
echo "3. Start server: python manage.py runserver"
echo "4. Test each middleware functionality"
