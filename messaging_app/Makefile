.PHONY: help install setup test test-ci run clean deploy

# Variables
PYTHON := python
PIP := pip
MANAGE := $(PYTHON) manage.py

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	$(PIP) install -r requirements.txt
	npm install -g newman newman-reporter-htmlextra

setup: install ## Setup the project (install + migrate + create users)
	@echo "🛠️  Setting up project..."
	$(MANAGE) migrate
	@echo "👥 Creating test users..."
	@$(MANAGE) shell < scripts/create_users.py
	@echo "✅ Setup complete!"

migrate: ## Run database migrations
	@echo "🗄️  Running migrations..."
	$(MANAGE) migrate

makemigrations: ## Create new migrations
	@echo "📝 Creating migrations..."
	$(MANAGE) makemigrations

run: ## Start the development server
	@echo "🚀 Starting server..."
	$(MANAGE) runserver 127.0.0.1:8000

test: ## Run automated tests with Newman
	@echo "🧪 Running tests..."
	@bash scripts/run_tests.sh

test-quick: ## Quick test without full setup
	@echo "⚡ Quick test..."
	@$(MANAGE) runserver 127.0.0.1:8000 & 
	@sleep 3
	@newman run post_man-Collections/Messaging_App_API_Tests.postman_collection.json -e post_man-Collections/local-environment.json
	@pkill -f "manage.py runserver"

test-ci: ## Run tests in CI environment
	@echo "🤖 Running CI tests..."
	@newman run post_man-Collections/Messaging_App_API_Tests.postman_collection.json \
		-e post_man-Collections/ci-environment.json \
		--reporters cli,htmlextra \
		--reporter-htmlextra-export test-reports/ci-report.html

shell: ## Open Django shell
	$(MANAGE) shell

superuser: ## Create a superuser
	$(MANAGE) createsuperuser

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage

deploy-staging: test ## Deploy to staging (after tests pass)
	@echo "🚀 Deploying to staging..."
	@bash scripts/deploy.sh staging

deploy-production: test ## Deploy to production (after tests pass)
	@echo "🚀 Deploying to production..."
	@bash scripts/deploy.sh production

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t messaging-app:latest .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker-compose up -d

docker-stop: ## Stop Docker container
	@echo "🐳 Stopping Docker container..."
	docker-compose down

logs: ## Show Django logs
	tail -f logs/django.log

format: ## Format code with black
	black .

lint: ## Run code linters
	flake8 .
	pylint chats/

requirements: ## Update requirements.txt
	$(PIP) freeze > requirements.txt

backup: ## Backup database
	@echo "💾 Backing up database..."
	$(MANAGE) dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 4 > backup-$(shell date +%Y%m%d-%H%M%S).json

restore: ## Restore database from backup (Usage: make restore FILE=backup.json)
	@echo "📥 Restoring database..."
	$(MANAGE) loaddata $(FILE)
