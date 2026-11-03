# ==============================================================================
# Ojas Ops: Open Operations Research & Optimization Framework
# Makefile for development, testing, linting, building, packaging, and releasing
#
# Author: Balu Varanasi <balu@chitram.ai>
# ==============================================================================

.DEFAULT_GOAL := help
SHELL         := /bin/bash
.SHELLFLAGS   := -eu -o pipefail -c

# Paths & Packaging Configuration
ROOT_DIR      := $(shell pwd)
PACKAGE_NAME  := ojas-ops
PACKAGE_DIR   := packages/ojas-ops
SRC_DIR       := $(PACKAGE_DIR)/src/ojas_ops
TESTS_DIR     := $(PACKAGE_DIR)/tests
EXAMPLES_DIR  := examples
DIST_DIR      := dist
DOCS_DIR      := ../docs
MKDOCS_CONFIG := ../mkdocs.yml

# Tooling & Environments (Auto-detecting virtualenv and system binaries)
UV            := $(shell which uv 2>/dev/null || echo $(HOME)/.local/bin/uv)
VENV          := $(ROOT_DIR)/.venv
PYTHON        := $(shell if [ -f $(VENV)/bin/python ]; then echo $(VENV)/bin/python; else which python3; fi)
PYTEST        := $(shell if [ -f $(VENV)/bin/pytest ]; then echo $(VENV)/bin/pytest; else which pytest; fi)
RUFF          := $(shell if [ -f $(VENV)/bin/ruff ]; then echo $(VENV)/bin/ruff; else which ruff; fi)
MYPY          := $(shell if [ -f $(VENV)/bin/mypy ]; then echo $(VENV)/bin/mypy; else which mypy; fi)

# Current Version Extraction
VERSION       := $(shell $(PYTHON) -c 'import tomllib; f=open("$(PACKAGE_DIR)/pyproject.toml","rb"); print(tomllib.load(f)["project"]["version"])' 2>/dev/null || echo "0.1.0")

# ANSI Terminal Colors
CYAN   := \033[36m
GREEN  := \033[32m
YELLOW := \033[33m
BLUE   := \033[34m
MAGENTA:= \033[35m
BOLD   := \033[1m
RESET  := \033[0m

# ==============================================================================
# Help Menu
# ==============================================================================

.PHONY: help
help: ## Show this help message with available commands
	@echo -e "$(BOLD)$(CYAN)Ojas Ops Development & Release Commands$(RESET)"
	@echo -e "Current Version: $(BOLD)$(GREEN)v$(VERSION)$(RESET) | Package: $(BOLD)$(YELLOW)$(PACKAGE_NAME)$(RESET)"
	@echo ""
	@echo -e "$(BOLD)Environment & Setup:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(install|sync|lock|update|venv)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(BOLD)Development Server:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(dev|run|runbolt|migrate)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(BOLD)Code Quality & Static Analysis:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(fmt|format|lint|lint-fix|typecheck|mypy|check)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(BOLD)Testing & Verification:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(test|test-fast|test-verbose|test-cov|test-adapters|test-calendars|test-constraints|test-solvers|test-simulation|test-models)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(BOLD)Examples & Execution:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(examples)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(BOLD)Documentation:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(docs-build|docs-serve)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(BOLD)Packaging & Build:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(clean|build|build-sdist|build-wheel|build-check)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""
	@echo -e "$(BOLD)Release & Versioning:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { \
		if ($$1 ~ /^(version|bump-patch|bump-minor|bump-major|tag|publish-dry-run|publish-test|publish|release)/) \
			printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 \
	}' $(MAKEFILE_LIST)
	@echo ""

# ==============================================================================
# Environment & Setup
# ==============================================================================

.PHONY: venv
venv: ## Verify or initialize the virtual environment
	@if [ ! -d "$(VENV)" ]; then \
		echo -e "$(YELLOW)Creating virtual environment with uv...$(RESET)"; \
		$(UV) venv $(VENV) --python 3.14; \
	fi

.PHONY: install
install: venv ## Install all workspace dependencies and editable packages
	@echo -e "$(GREEN)Syncing workspace dependencies with uv...$(RESET)"
	@$(UV) sync --all-packages --all-extras

.PHONY: sync
sync: ## Synchronize environment strictly against uv.lock
	@echo -e "$(GREEN)Syncing locked environment...$(RESET)"
	@$(UV) sync

.PHONY: lock
lock: ## Update uv.lock without upgrading dependency versions
	@echo -e "$(GREEN)Locking workspace dependencies...$(RESET)"
	@$(UV) lock

.PHONY: update
update: ## Upgrade all dependencies and regenerate uv.lock
	@echo -e "$(YELLOW)Upgrading all dependencies...$(RESET)"
	@$(UV) lock --upgrade
	@$(UV) sync

# ==============================================================================
# Development Server & Services
# ==============================================================================

.PHONY: dev run runbolt migrate
migrate: venv ## Apply database migrations in apps/sandbox
	@echo -e "$(GREEN)Applying database migrations...$(RESET)"
	@cd apps/sandbox && $(PYTHON) manage.py migrate --no-input

dev: run ## Alias for run
run: runbolt ## Alias for runbolt
runbolt: migrate ## Start Django-Bolt API development server on http://127.0.0.1:8000
	@echo -e "$(BOLD)$(CYAN)Starting Django-Bolt API server on http://127.0.0.1:8000...$(RESET)"
	@cd apps/sandbox && $(PYTHON) manage.py runbolt -b 0.0.0.0 -p 8000

# ==============================================================================
# Code Quality, Formatting & Static Analysis
# ==============================================================================

.PHONY: fmt format
fmt: format ## Alias for format
format: ## Format Python source files using Ruff
	@echo -e "$(GREEN)Formatting codebase with Ruff...$(RESET)"
	@$(RUFF) format $(ROOT_DIR)

.PHONY: lint
lint: ## Run Ruff linter checks
	@echo -e "$(GREEN)Checking code style and imports with Ruff...$(RESET)"
	@$(RUFF) check $(ROOT_DIR)

.PHONY: lint-fix
lint-fix: ## Automatically fix autofixable Ruff lint violations
	@echo -e "$(YELLOW)Auto-fixing lint violations with Ruff...$(RESET)"
	@$(RUFF) check --fix $(ROOT_DIR)

.PHONY: typecheck mypy
typecheck: mypy ## Alias for mypy
mypy: ## Run static type checking with Mypy
	@echo -e "$(GREEN)Running static type analysis with Mypy...$(RESET)"
	@$(MYPY) $(SRC_DIR)

.PHONY: check
check: ## Run formatting check, linter, and type checker in sequence
	@echo -e "$(BOLD)$(CYAN)=== Running Comprehensive Code Quality Gates ===$(RESET)"
	@echo -e "$(GREEN)[1/3] Ruff format check...$(RESET)"
	@$(RUFF) format --check $(ROOT_DIR)
	@echo -e "$(GREEN)[2/3] Ruff lint check...$(RESET)"
	@$(RUFF) check $(ROOT_DIR)
	@echo -e "$(GREEN)[3/3] Mypy type analysis...$(RESET)"
	@$(MYPY) $(SRC_DIR)
	@echo -e "$(BOLD)$(GREEN)All quality gates passed successfully!$(RESET)"

# ==============================================================================
# Testing & Verification
# ==============================================================================

.PHONY: test
test: ## Run the full test suite with pytest
	@echo -e "$(GREEN)Running test suite...$(RESET)"
	@$(PYTEST) $(TESTS_DIR)

.PHONY: test-fast
test-fast: ## Run pytest in quiet, fail-fast mode (-x -q)
	@echo -e "$(YELLOW)Running fail-fast test gate...$(RESET)"
	@$(PYTEST) -x -q $(TESTS_DIR)

.PHONY: test-verbose
test-verbose: ## Run pytest with verbose output and stdout captured (-vv -s)
	@$(PYTEST) -vv -s $(TESTS_DIR)

.PHONY: test-cov
test-cov: ## Run test suite with code coverage report
	@echo -e "$(GREEN)Running tests with coverage...$(RESET)"
	@if $(PYTEST) --cov=ojas_ops --help >/dev/null 2>&1; then \
		$(PYTEST) --cov=ojas_ops --cov-report=term-missing --cov-report=html:htmlcov $(TESTS_DIR); \
		echo -e "$(GREEN)Coverage HTML report written to htmlcov/index.html$(RESET)"; \
	else \
		echo -e "$(YELLOW)pytest-cov not found, running standard test suite...$(RESET)"; \
		$(PYTEST) $(TESTS_DIR); \
	fi

.PHONY: test-adapters
test-adapters: ## Run domain adapter tests
	@$(PYTEST) -v $(TESTS_DIR)/test_adapters.py

.PHONY: test-calendars
test-calendars: ## Run standard & cultural calendar tests
	@$(PYTEST) -v $(TESTS_DIR)/test_calendars.py

.PHONY: test-constraints
test-constraints: ## Run constraint formulation tests
	@$(PYTEST) -v $(TESTS_DIR)/test_constraints.py

.PHONY: test-solvers
test-solvers: ## Run CP-SAT solver backend tests
	@$(PYTEST) -v $(TESTS_DIR)/test_solvers.py

.PHONY: test-simulation
test-simulation: ## Run scenario simulation & rescheduling tests
	@$(PYTEST) -v $(TESTS_DIR)/test_simulation.py

.PHONY: test-models
test-models: ## Run core domain model & serialization tests
	@$(PYTEST) -v $(TESTS_DIR)/test_models.py

# ==============================================================================
# Examples Execution & Validation
# ==============================================================================

.PHONY: examples
examples: ## Execute all 8 domain examples and verify end-to-end solutions
	@echo -e "$(BOLD)$(CYAN)=== Running All Domain Examples ===$(RESET)"
	@for ex in $(EXAMPLES_DIR)/*/main.py; do \
		echo -e "$(GREEN)--> Executing $$ex$(RESET)"; \
		$(PYTHON) "$$ex" || exit 1; \
	done
	@echo -e "$(BOLD)$(GREEN)All domain examples executed and verified successfully!$(RESET)"

# ==============================================================================
# Documentation
# ==============================================================================

.PHONY: docs-build
docs-build: ## Build static documentation site with MkDocs
	@echo -e "$(GREEN)Building documentation with MkDocs...$(RESET)"
	@if [ -f "$(VENV)/bin/mkdocs" ]; then \
		$(VENV)/bin/mkdocs build -f $(MKDOCS_CONFIG); \
	else \
		$(UV) run mkdocs build -f $(MKDOCS_CONFIG); \
	fi

.PHONY: docs-serve
docs-serve: ## Serve documentation locally on http://127.0.0.1:8000
	@echo -e "$(GREEN)Serving documentation with MkDocs...$(RESET)"
	@if [ -f "$(VENV)/bin/mkdocs" ]; then \
		$(VENV)/bin/mkdocs serve -f $(MKDOCS_CONFIG); \
	else \
		$(UV) run mkdocs serve -f $(MKDOCS_CONFIG); \
	fi

# ==============================================================================
# Packaging & Build
# ==============================================================================

.PHONY: clean
clean: ## Remove build artifacts, wheels, tarballs, and cache directories
	@echo -e "$(YELLOW)Cleaning build artifacts and caches...$(RESET)"
	@rm -rf $(DIST_DIR) build/ *.egg-info packages/*/*.egg-info
	@rm -rf .pytest_cache packages/*/.pytest_cache
	@rm -rf .ruff_cache packages/*/.ruff_cache
	@rm -rf .mypy_cache packages/*/.mypy_cache
	@rm -rf htmlcov .coverage
	@rm -rf site/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.py[cod]" -delete 2>/dev/null || true
	@echo -e "$(GREEN)Workspace cleaned.$(RESET)"

.PHONY: build
build: clean ## Build both source distribution (sdist) and binary wheel (wheel)
	@echo -e "$(BOLD)$(CYAN)Building package $(PACKAGE_NAME) v$(VERSION)...$(RESET)"
	@$(UV) build --package $(PACKAGE_NAME)
	@echo -e "$(BOLD)$(GREEN)Build artifacts created in $(DIST_DIR)/:$(RESET)"
	@ls -lh $(DIST_DIR)

.PHONY: build-sdist
build-sdist: ## Build only source distribution (.tar.gz)
	@$(UV) build --package $(PACKAGE_NAME) --sdist

.PHONY: build-wheel
build-wheel: ## Build only binary wheel (.whl)
	@$(UV) build --package $(PACKAGE_NAME) --wheel

.PHONY: build-check
build-check: build ## Verify integrity and inspect contents of built distribution packages
	@echo -e "$(BOLD)$(CYAN)Verifying build artifacts in $(DIST_DIR)/...$(RESET)"
	@for f in $(DIST_DIR)/*.tar.gz; do \
		echo -e "$(GREEN)--> Inspecting Source Distribution: $$f$(RESET)"; \
		tar -tzf "$$f" | head -n 25; \
		echo "    ..."; \
	done
	@for w in $(DIST_DIR)/*.whl; do \
		echo -e "$(GREEN)--> Inspecting Wheel: $$w$(RESET)"; \
		$(PYTHON) -m zipfile -l "$$w" | head -n 25; \
		echo "    ..."; \
	done
	@echo -e "$(BOLD)$(GREEN)All build artifacts successfully verified!$(RESET)"

# ==============================================================================
# Release & Versioning
# ==============================================================================

.PHONY: version
version: ## Display current package version
	@echo "v$(VERSION)"

.PHONY: bump-patch
bump-patch: ## Bump patch version (x.y.Z -> x.y.Z+1) in pyproject.toml files
	@$(PYTHON) -c 'import re; \
	def bump(): \
	  for p in ["pyproject.toml", "$(PACKAGE_DIR)/pyproject.toml"]: \
	    c = open(p).read(); \
	    m = re.search(r"version\s*=\s*\"(\d+)\.(\d+)\.(\d+)\"", c); \
	    maj, mi, pa = map(int, m.groups()); \
	    nv = f"{maj}.{mi}.{pa+1}"; \
	    open(p, "w").write(re.sub(r"version\s*=\s*\"\d+\.\d+\.\d+\"", f"version = \"{nv}\"", c, count=1)); \
	    print(f"Bumped {p} -> {nv}"); \
	bump()'

.PHONY: bump-minor
bump-minor: ## Bump minor version (x.Y.0 -> x.Y+1.0) in pyproject.toml files
	@$(PYTHON) -c 'import re; \
	def bump(): \
	  for p in ["pyproject.toml", "$(PACKAGE_DIR)/pyproject.toml"]: \
	    c = open(p).read(); \
	    m = re.search(r"version\s*=\s*\"(\d+)\.(\d+)\.(\d+)\"", c); \
	    maj, mi, pa = map(int, m.groups()); \
	    nv = f"{maj}.{mi+1}.0"; \
	    open(p, "w").write(re.sub(r"version\s*=\s*\"\d+\.\d+\.\d+\"", f"version = \"{nv}\"", c, count=1)); \
	    print(f"Bumped {p} -> {nv}"); \
	bump()'

.PHONY: bump-major
bump-major: ## Bump major version (X.0.0 -> X+1.0.0) in pyproject.toml files
	@$(PYTHON) -c 'import re; \
	def bump(): \
	  for p in ["pyproject.toml", "$(PACKAGE_DIR)/pyproject.toml"]: \
	    c = open(p).read(); \
	    m = re.search(r"version\s*=\s*\"(\d+)\.(\d+)\.(\d+)\"", c); \
	    maj, mi, pa = map(int, m.groups()); \
	    nv = f"{maj+1}.0.0"; \
	    open(p, "w").write(re.sub(r"version\s*=\s*\"\d+\.\d+\.\d+\"", f"version = \"{nv}\"", c, count=1)); \
	    print(f"Bumped {p} -> {nv}"); \
	bump()'

.PHONY: tag
tag: ## Create and annotate a git release tag v$(VERSION)
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo -e "$(RED)Error: Git working tree is dirty. Please commit or stash changes before tagging.$(RESET)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)Creating git release tag v$(VERSION)...$(RESET)"
	@git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	@echo -e "$(BOLD)$(GREEN)Tagged commit as v$(VERSION). Push with 'git push origin v$(VERSION)'.$(RESET)"

.PHONY: publish-dry-run
publish-dry-run: build ## Perform a dry run of PyPI publication without uploading
	@echo -e "$(CYAN)Performing publishing dry-run...$(RESET)"
	@$(UV) publish --dry-run $(DIST_DIR)/*
	@echo -e "$(BOLD)$(GREEN)Publish dry-run succeeded!$(RESET)"

.PHONY: publish-test
publish-test: build ## Publish built distribution packages to TestPyPI
	@echo -e "$(YELLOW)Publishing packages to TestPyPI...$(RESET)"
	@$(UV) publish --publish-url https://test.pypi.org/legacy/ $(DIST_DIR)/*

.PHONY: publish
publish: build ## Publish built distribution packages to PyPI
	@echo -e "$(BOLD)$(GREEN)Publishing package v$(VERSION) to PyPI...$(RESET)"
	@$(UV) publish $(DIST_DIR)/*

.PHONY: release
release: ## Complete release pipeline: checks, tests, examples, build, verification, and dry-run
	@echo -e "$(BOLD)$(MAGENTA)================================================$(RESET)"
	@echo -e "$(BOLD)$(MAGENTA)   Ojas Ops Full Release Verification Pipeline  $(RESET)"
	@echo -e "$(BOLD)$(MAGENTA)================================================$(RESET)"
	@$(MAKE) check
	@$(MAKE) test
	@$(MAKE) examples
	@$(MAKE) build-check
	@$(MAKE) publish-dry-run
	@echo ""
	@echo -e "$(BOLD)$(GREEN)=== Release pipeline v$(VERSION) completed with ZERO errors! ===$(RESET)"
	@echo -e "Ready to tag and publish: run $(CYAN)make tag$(RESET) and $(CYAN)make publish$(RESET)."

