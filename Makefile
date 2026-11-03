# ==============================================================================
# Ojas Ops Monorepo — Root Orchestration Makefile
# Backend targets delegate to python/Makefile; Frontend scripts to typescript/
# ==============================================================================

SHELL := /bin/zsh
.DEFAULT_GOAL := help
.PHONY: help test test-fast check lint fmt gates dev dev-backend dev-frontend clean-caches clean

dev-backend: ## Run backend Django-Bolt API server on http://127.0.0.1:8000
	$(MAKE) -C python dev

dev-frontend: ## Run frontend Next.js Ops Studio on http://localhost:5900
	cd typescript && pnpm dev

dev: ## Instructions for running backend and frontend development servers concurrently
	@echo "\033[1;36m=== Ojas Ops Development Servers ===\033[0m"
	@echo "Open two terminal sessions to run both servers concurrently:"
	@echo "  \033[32mTerminal 1 (Backend API on http://127.0.0.1:8000):\033[0m"
	@echo "    make dev-backend"
	@echo "  \033[32mTerminal 2 (Frontend Ops Studio on http://localhost:5900):\033[0m"
	@echo "    make dev-frontend"
	@echo ""
	@echo "Direct commands:"
	@echo "  Backend:  cd python && uv run python apps/sandbox/manage.py runbolt"
	@echo "  Frontend: cd typescript && pnpm dev"

test: ## Run backend Python test suite (pass ARGS=... for specific pytest flags)
	$(MAKE) -C python test ARGS="$(ARGS)"

test-fast: ## Fast backend test run
	$(MAKE) -C python test-fast

check: ## Run all static checks (Python ruff/mypy + TypeScript gates)
	$(MAKE) -C python check
	@if [ -d typescript/node_modules ]; then $(MAKE) gates; fi

lint: ## Lint all workspaces
	$(MAKE) -C python lint
	@if [ -d typescript/node_modules ]; then cd typescript && pnpm lint; fi

fmt: ## Format all workspaces
	$(MAKE) -C python fmt
	@if [ -d typescript/node_modules ]; then cd typescript && pnpm format; fi

gates: ## Frontend gates: type-check + lint typescript workspace
	cd typescript && pnpm check-types && pnpm lint

clean-caches: ## Clean build and lint caches across python and typescript
	rm -rf python/.ruff_cache python/.mypy_cache python/.pytest_cache
	@if [ -d typescript ]; then cd typescript && rm -rf .turbo node_modules/.cache apps/*/.next; fi

help: ## Show this help message
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

