# ==============================================================================
# Ojas Ops Monorepo — Root Orchestration Makefile
# Backend targets delegate to python/Makefile; Frontend scripts to typescript/
# ==============================================================================

SHELL := /bin/zsh
.DEFAULT_GOAL := help
.PHONY: help test test-fast check lint fmt gates dev clean-caches clean

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

