
TEX_WORKDIR = $(CURDIR)/docs
BUILD_DIR = $(TEX_WORKDIR)/_build
OUT_DIR = $(CURDIR)/pdf
TEX_FILES = $(TEX_WORKDIR)/*.tex
TEX_MAIN = $(TEX_WORKDIR)/main.tex
ZIP_FILE = $(CURDIR)/tp2.zip
RESULTS_DIR = $(TEX_WORKDIR)/results
DADOS_DIR = $(TEX_WORKDIR)/resultados
SRC_FILES = $(wildcard $(CURDIR)/src/tp2/*.py)
ANALISE_STAMP = $(RESULTS_DIR)/.analise.stamp

# Imagem TeX Live usada no build final (https://github.com/xu-cheng/latex-docker)
LATEX_IMAGE ?= ghcr.io/xu-cheng/texlive-full:latest
CONTAINER ?= docker
# Em runtime rootless o root do container ja mapeia para o usuario do host;
# caso contrario, roda como o usuario atual para os arquivos gerados nao ficarem como root.
CONTAINER_USER ?= $(if $(shell $(CONTAINER) info 2>/dev/null | grep -iE 'rootless(: *true)?$$'),,--user $(shell id -u):$(shell id -g))

.PHONY: help
help: ## Mostra esta ajuda
	@echo "Uso: make [alvo]"
	@echo ""
	@echo "Alvos disponíveis:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: format
format: ## Formata o código com ruff
	uv run ruff format src tests
	uv run ruff check --fix src tests

.PHONY: lint
lint: ## Roda o linter (ruff)
	uv run ruff check src tests

.PHONY: test
test: ## Roda os testes com pytest
	uv run pytest tests -v

# Experimentos: cada alvo grava seus CSVs em docs/resultados.

.PHONY: resultado-aleatoria
resultado-aleatoria: ## Roda a busca aleatoria (valida o formato dos CSVs)
	uv run python -m tp2.experimento aleatoria -o $(DADOS_DIR)

.PHONY: resultado-local
resultado-local: ## Roda a busca local (GD + random restart, vizinhancas, incremental)
	uv run python -m tp2.experimento local -o $(DADOS_DIR)

.PHONY: resultado-tempera
resultado-tempera: ## Roda o simulated annealing
	uv run python -m tp2.experimento tempera -o $(DADOS_DIR)

.PHONY: resultado-genetico
resultado-genetico: ## Roda o algoritmo genetico e o experimento adicional
	uv run python -m tp2.experimento genetico -o $(DADOS_DIR)

.PHONY: resultado-todos
resultado-todos: resultado-local resultado-tempera resultado-genetico ## Rodada final completa

.PHONY: resultado-figuras
resultado-figuras: analise ## Gera as figuras a partir dos CSVs (alias de analise)

.PHONY: analise
analise: $(ANALISE_STAMP) ## Gera os graficos da analise em docs/results (usados no relatorio)

$(ANALISE_STAMP): $(SRC_FILES) $(wildcard $(DADOS_DIR)/*.csv)
	uv run python -m tp2.analise -o $(RESULTS_DIR)
	touch $@

.PHONY: docs
docs: docs-clean analise ## Build final da documentacao/relatorio (via container)
	@# MSYS_NO_PATHCONV evita que o Git Bash (Windows) reescreva os caminhos /workdir e /tmp
	MSYS_NO_PATHCONV=1 $(CONTAINER) run --rm \
		$(CONTAINER_USER) -e HOME=/tmp \
		-v $(CURDIR):/workdir:z -w /workdir/docs \
		$(LATEX_IMAGE) \
		latexmk -interaction=nonstopmode -halt-on-error

.PHONY: docs-live
docs-live: docs-clean analise ## Build-dinamico da documentacao/relatorio (nativo)
	cd $(TEX_WORKDIR) && latexmk -pvc

.PHONY: docs-clean
docs-clean: ## Remove os artefatos de build do relatorio e os graficos gerados
	rm -rf $(BUILD_DIR) $(OUT_DIR) $(RESULTS_DIR)

.PHONY: docs-format
docs-format: ## Formata os arquivos .tex com latexindent
	mkdir -p $(BUILD_DIR)
	for f in $(TEX_FILES); do \
		latexindent -w -s -c=$(BUILD_DIR) "$$f"; \
	done

.PHONY: zip
zip: ## Empacota src, tests, pyproject.toml e README.md em um .zip
	rm -f $(ZIP_FILE)
	zip -r $(ZIP_FILE) src tests pyproject.toml README.md -x '*__pycache__*' -x '*.pyc'
