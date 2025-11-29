#!/bin/bash
# Production deployment script

set -e

echo "🚀 Starting deployment process..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
ENVIRONMENT=${1:-staging}  # staging or production
REPO_URL="https://github.com/jalloh19/alx-backend-python.git"
APP_DIR="/var/www/messaging_app"

echo -e "${BLUE}Deploying to: ${ENVIRONMENT}${NC}"

# Step 1: Run tests first
echo -e "${YELLOW}⚠️  Running tests before deployment...${NC}"
./scripts/run_tests.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests failed! Aborting deployment.${NC}"
    exit 1
fi

# Step 2: Pull latest code
echo -e "${BLUE}📥 Pulling latest code from GitHub...${NC}"
git pull origin main

# Step 3: Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt --no-cache-dir

# Step 4: Run migrations
echo -e "${BLUE}🗄️  Running database migrations...${NC}"
python manage.py migrate --no-input

# Step 5: Collect static files
echo -e "${BLUE}📁 Collecting static files...${NC}"
python manage.py collectstatic --no-input

# Step 6: Restart services
echo -e "${BLUE}🔄 Restarting services...${NC}"
if [ "$ENVIRONMENT" = "production" ]; then
    sudo systemctl restart gunicorn
    sudo systemctl restart nginx
else
    sudo systemctl restart gunicorn-staging
fi

# Step 7: Health check
echo -e "${BLUE}🏥 Running health check...${NC}"
sleep 3

if [ "$ENVIRONMENT" = "production" ]; then
    HEALTH_URL="https://api.yourdomain.com/api/health/"
else
    HEALTH_URL="https://staging.yourdomain.com/api/health/"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Deployment successful! Service is healthy.${NC}"
else
    echo -e "${RED}❌ Deployment failed! Health check returned: $HTTP_CODE${NC}"
    exit 1
fi

# Step 8: Tag the release
TAG="release-$(date +%Y%m%d-%H%M%S)"
git tag -a $TAG -m "Automated deployment to $ENVIRONMENT"
git push origin $TAG

echo -e "${GREEN}🎉 Deployment complete! Tagged as: $TAG${NC}"
