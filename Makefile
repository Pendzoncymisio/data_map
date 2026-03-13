.PHONY: help install-dev test test-unit test-integration test-e2e lint format typecheck coverage

# ── Default target ────────────────────────────────────────────────────────────
help:
	@echo "Available targets:"
	@echo "  install-dev      Install all dev dependencies and configure pre-commit"
	@echo "  test             Run the full test suite (headless)"
	@echo "  test-unit        Run unit + Qt unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e         Run end-to-end tests only"
	@echo "  lint             Check code with ruff"
	@echo "  format           Auto-format code with ruff"
	@echo "  typecheck        Run mypy on non-Qt modules"
	@echo "  coverage         Run tests and produce an HTML coverage report"

# ── Setup ─────────────────────────────────────────────────────────────────────
install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-qt pytest-cov pytest-mock ruff mypy pre-commit
	pre-commit install

# ── Testing ───────────────────────────────────────────────────────────────────
PYTEST_FLAGS ?= -v --tb=short
QT_ENV       = QT_QPA_PLATFORM=offscreen

test:
	$(QT_ENV) python3 -m pytest $(PYTEST_FLAGS)

test-unit:
	$(QT_ENV) python3 -m pytest $(PYTEST_FLAGS) -m "unit or qt" --ignore=tests/e2e

test-integration:
	$(QT_ENV) python3 -m pytest $(PYTEST_FLAGS) -m integration

test-e2e:
	$(QT_ENV) python3 -m pytest $(PYTEST_FLAGS) tests/e2e/

# ── Quality ───────────────────────────────────────────────────────────────────
lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy load_config.py save_documentation.py load_documentation.py theme.py

coverage:
	$(QT_ENV) python3 -m pytest --cov --cov-report=html --cov-report=term-missing
	@echo "HTML report: htmlcov/index.html"
