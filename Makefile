.DEFAULT_GOAL := help

.PHONY: help fmt lint test

help: ## Mostra esta ajuda
	@echo "Uso: make [alvo]"
	@echo ""
	@echo "Alvos disponíveis:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

format: ## Formata o código com ruff
	uv run ruff format src
	uv run ruff check --fix src

lint: ## Roda o linter (ruff) e o typecheck (mypy)
	uv run ruff check src
	uv run mypy src

test: ## Roda os testes com pytest
	uv run pytest src/ponte_tocha/*.py
