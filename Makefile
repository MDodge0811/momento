.PHONY: help test test-verbose test-coverage test-fast install-test-deps clean install

help:  ## Show this help message
	@echo "Eidex - Branch-aware AI logging library"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install-test-deps:  ## Install testing dependencies
	pip install -r requirements-test.txt

test: install-test-deps  ## Run tests
	python -m pytest tests/ -v

test-verbose: install-test-deps  ## Run tests with verbose output
	python -m pytest tests/ -vv --tb=long

test-coverage: install-test-deps  ## Run tests with coverage report
	python -m pytest tests/ -v --cov=eidex --cov-report=term-missing --cov-report=html:htmlcov

test-fast: install-test-deps  ## Run tests quickly (minimal output)
	python -m pytest tests/ -q

install:  ## Install the library in development mode
	pip install -e .

clean:  ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:  ## Run linting checks
	@echo "Running flake8..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 .; \
	else \
		echo "flake8 not found. Install with: pip install flake8"; \
	fi

lint-check:  ## Check linting without fixing
	@echo "Checking code quality with flake8..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 --count --statistics .; \
	else \
		echo "flake8 not found. Install with: pip install flake8"; \
	fi

type-check:  ## Run type checking with mypy
	@echo "Running type checking with mypy..."
	@if command -v mypy >/dev/null 2>&1; then \
		mypy .; \
	else \
		echo "mypy not found. Install with: pip install mypy"; \
	fi

type-check-strict:  ## Run strict type checking with mypy
	@echo "Running strict type checking with mypy..."
	@if command -v mypy >/dev/null 2>&1; then \
		mypy --strict .; \
	else \
		echo "mypy not found. Install with: pip install mypy"; \
	fi

format:  ## Format code with black and isort
	@echo "Running isort..."
	@if command -v isort >/dev/null 2>&1; then \
		isort .; \
	else \
		echo "isort not found. Install with: pip install isort"; \
	fi
	@echo "Running black..."
	@if command -v black >/dev/null 2>&1; then \
		black .; \
	else \
		echo "black not found. Install with: pip install black"; \
	fi

format-check:  ## Check if code is formatted with black and isort
	@echo "Checking import sorting..."
	@if command -v isort >/dev/null 2>&1; then \
		isort --check-only --diff .; \
	else \
		echo "isort not found. Install with: pip install isort"; \
	fi
	@echo "Checking code formatting..."
	@if command -v black >/dev/null 2>&1; then \
		black --check .; \
	else \
		echo "black not found. Install with: pip install black"; \
	fi

imports:  ## Sort imports with isort
	@echo "Sorting imports..."
	@if command -v isort >/dev/null 2>&1; then \
		isort .; \
	else \
		echo "isort not found. Install with: pip install isort"; \
	fi

check: test lint type-check  ## Run tests, linting, and type checking
	@echo "✅ All checks passed!"

dev-setup: install-test-deps install  ## Set up development environment
	@echo "✅ Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make check' to run tests and linting"
