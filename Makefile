.PHONY: help up down build test coverage lint format clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Start all services with Docker Compose
	docker-compose up --build

down: ## Stop all services
	docker-compose down

build: ## Build all Docker images
	docker-compose build

test: ## Run backend unit tests with coverage
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=60

coverage: ## Generate HTML coverage report
	cd backend && python -m pytest tests/ --cov=app --cov-report=html && echo "Report: backend/htmlcov/index.html"

lint: ## Run linters (flake8 + mypy)
	cd backend && python -m flake8 app/ tests/ --max-line-length=100
	cd backend && python -m mypy app/ --ignore-missing-imports

format: ## Format code with black and isort
	cd backend && python -m black app/ tests/ --line-length=100
	cd backend && python -m isort app/ tests/

clean: ## Remove build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage 2>/dev/null || true
