# 🤖 Automation Guide: Backend → Postman → GitHub → Production

This guide covers the complete automation workflow for your messaging app.

## 📋 Table of Contents
1. [Local Development Automation](#local-development)
2. [GitHub Actions CI/CD](#github-actions)
3. [Automated Testing](#automated-testing)
4. [Production Deployment](#production-deployment)
5. [Monitoring & Alerts](#monitoring)

---

## 🖥️ Local Development Automation

### Quick Start with Makefile

Install Newman (Postman CLI):
```bash
npm install -g newman newman-reporter-htmlextra
```

Available commands:
```bash
# Setup everything (install, migrate, create users)
make setup

# Run development server
make run

# Run all tests automatically
make test

# Deploy to staging (runs tests first)
make deploy-staging

# See all available commands
make help
```

### Automated Test Script

Run complete test workflow:
```bash
bash scripts/run_tests.sh
```

This automatically:
1. ✅ Applies database migrations
2. ✅ Creates test users (alice, bob)
3. ✅ Starts Django server
4. ✅ Runs all Postman tests
5. ✅ Generates HTML report
6. ✅ Cleans up (stops server)

### Environment Files

**Local Development** (`local-environment.json`):
- Uses `http://127.0.0.1:8000/api`
- Test users: alice, bob

**CI Environment** (`ci-environment.json`):
- Uses `http://localhost:8000/api`
- Test users: testuser1, testuser2

Import in Postman: Settings → Environments → Import

---

## 🚀 GitHub Actions CI/CD

### Automatic Testing on Push

**File**: `.github/workflows/api-tests.yml`

Triggers:
- ✅ Every push to `main` or `develop`
- ✅ Every pull request to these branches

What it does:
1. Sets up PostgreSQL database
2. Installs Python dependencies
3. Runs migrations
4. Creates test users
5. Starts Django server
6. Runs Newman tests
7. Uploads HTML report as artifact
8. Comments on PR with results

### View Test Results

1. Go to your repo: `https://github.com/jalloh19/alx-backend-python`
2. Click **Actions** tab
3. Select the latest workflow run
4. Download **newman-test-report** artifact
5. Open `newman-report.html` in browser

### Setup Required Secrets

Go to: `Settings → Secrets and variables → Actions`

Add these secrets:
```
AWS_ACCESS_KEY_ID          # For production deployment
AWS_SECRET_ACCESS_KEY      # For production deployment
SLACK_WEBHOOK              # For notifications (optional)
```

---

## 🧪 Automated Testing

### Running Tests Locally

**Option 1: Full automation**
```bash
make test
```

**Option 2: Quick test (server must be running)**
```bash
make test-quick
```

**Option 3: Manual Newman**
```bash
# Start server first
python manage.py runserver

# In another terminal
newman run post_man-Collections/Messaging_App_API_Tests.postman_collection.json \
  -e post_man-Collections/local-environment.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export test-report.html
```

### Test Reports

Reports are saved in `test-reports/` directory:
- Timestamped HTML reports
- Shows pass/fail for each test
- Request/response details
- Performance metrics

### Integration with Postman

**Sync collection to Postman Cloud:**
1. Open Postman
2. Import collection
3. Click collection → Share
4. Enable "Watch collection"
5. Generate API key
6. Use in GitHub Actions:
   ```yaml
   - name: Run Postman tests
     env:
       POSTMAN_API_KEY: ${{ secrets.POSTMAN_API_KEY }}
     run: newman run https://api.getpostman.com/collections/YOUR_COLLECTION_ID
   ```

---

## 🌐 Production Deployment

### Docker Deployment

**Build and run:**
```bash
make docker-build
make docker-run
```

**Or use docker-compose:**
```bash
docker-compose up -d
```

Includes:
- PostgreSQL database
- Django app (Gunicorn)
- Nginx reverse proxy

**Access:**
- API: `http://localhost:8000/api/`
- Admin: `http://localhost:8000/admin/`

### Manual Deployment Script

```bash
# Deploy to staging
bash scripts/deploy.sh staging

# Deploy to production
bash scripts/deploy.sh production
```

Script workflow:
1. ✅ Runs all tests
2. ✅ Pulls latest code
3. ✅ Installs dependencies
4. ✅ Runs migrations
5. ✅ Collects static files
6. ✅ Restarts services
7. ✅ Health check
8. ✅ Creates git tag

### AWS ECS Deployment

**File**: `.github/workflows/deploy-production.yml`

Triggers:
- When you publish a release on GitHub
- Manual workflow dispatch

Deploys to:
- AWS ECS (Elastic Container Service)
- Uses Docker image
- Automatic rollback on failure

**Setup:**
1. Create ECS cluster: `messaging-cluster`
2. Create ECS service: `messaging-service`
3. Add secrets to GitHub (see above)

---

## 📊 Monitoring & Alerts

### Health Check Endpoint

Add to `chats/views.py`:
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return Response({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return Response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
```

Add to `chats/urls.py`:
```python
urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    # ... other patterns
]
```

### Automated Monitoring

**Setup cron job for health checks:**
```bash
# Edit crontab
crontab -e

# Add this line (check every 5 minutes)
*/5 * * * * curl -f https://api.yourdomain.com/api/health/ || echo "API Down!" | mail -s "Alert: API Health Check Failed" your@email.com
```

### Slack Notifications

Add to GitHub Actions:
```yaml
- name: Notify on Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: |
      Tests ${{ job.status }}
      Commit: ${{ github.sha }}
      Author: ${{ github.actor }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🔄 Complete Automation Workflow

```
┌─────────────────┐
│  Code Change    │
│  (git push)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ GitHub Actions  │
│ Triggered       │
└────────┬────────┘
         │
         ├─► Run Migrations
         ├─► Create Test Users
         ├─► Start Server
         ├─► Newman Tests
         │
         ▼
┌─────────────────┐
│  Tests Pass?    │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    │         └─► ❌ Fail PR
    │             └─► Comment on PR
    │             └─► Send notification
    │
    ▼
┌─────────────────┐
│  Merge to Main  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Release │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Deploy to Prod  │
│ (Automatic)     │
└────────┬────────┘
         │
         ├─► Build Docker Image
         ├─► Push to ECR
         ├─► Update ECS Service
         ├─► Run Smoke Tests
         │
         ▼
┌─────────────────┐
│ ✅ Deployed!    │
│ 📊 Monitoring   │
└─────────────────┘
```

---

## 🎯 Best Practices

### 1. Branch Protection Rules

Settings → Branches → Add rule for `main`:
- ✅ Require status checks before merging
- ✅ Require branches to be up to date
- ✅ Require tests to pass (GitHub Actions)
- ✅ Require pull request reviews

### 2. Semantic Versioning

Tag releases properly:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 3. Environment Variables

Never commit secrets! Use:
- `.env` files (add to `.gitignore`)
- GitHub Secrets for CI/CD
- AWS Secrets Manager for production

### 4. Database Backups

Automated daily backups:
```bash
# Add to crontab
0 2 * * * cd /path/to/app && make backup
```

### 5. Rollback Strategy

Quick rollback:
```bash
# Find previous tag
git tag -l

# Rollback to previous version
git checkout v1.0.0
make deploy-production
```

---

## 📚 Additional Resources

- **Newman Documentation**: https://learning.postman.com/docs/running-collections/using-newman-cli/
- **GitHub Actions**: https://docs.github.com/en/actions
- **Docker Compose**: https://docs.docker.com/compose/
- **AWS ECS**: https://aws.amazon.com/ecs/

---

## 🆘 Troubleshooting

### Newman not found
```bash
npm install -g newman newman-reporter-htmlextra
```

### Tests fail locally but pass in CI
- Check Python version (should match CI)
- Check dependencies versions
- Ensure database is clean

### Deployment fails
1. Check GitHub Actions logs
2. Verify AWS credentials
3. Check ECS cluster status
4. Review application logs

### Database issues
```bash
# Reset database
python manage.py flush --no-input
python manage.py migrate
make setup
```

---

## 🎉 Quick Start Checklist

- [ ] Install Newman: `npm install -g newman newman-reporter-htmlextra`
- [ ] Run setup: `make setup`
- [ ] Run tests: `make test`
- [ ] Commit `.github/workflows/` files
- [ ] Push to GitHub
- [ ] Check Actions tab for test results
- [ ] Setup branch protection
- [ ] Add GitHub secrets for deployment
- [ ] Create first release
- [ ] Deploy to production! 🚀

---

**Need Help?**
- Check the logs: `make logs`
- Run health check: `curl http://localhost:8000/api/health/`
- View test reports in `test-reports/` directory
