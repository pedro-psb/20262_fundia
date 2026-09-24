
TEX_WORKDIR = $(CURDIR)/docs
BUILD_DIR = $(TEX_WORKDIR)/_build
OUT_DIR = $(CURDIR)/pdf
TEX_FILES = $(TEX_WORKDIR)/*.tex
TEX_MAIN = $(TEX_WORKDIR)/main.tex
ZIP_FILE = $(CURDIR)/tp2.zip
RESULTS_DIR = $(TEX_WORKDIR)/results
SRC_FILES = $(wildcard $(CURDIR)/src/tp2/*.py)
ANALISE_STAMP = $(RESULTS_DIR)/.analise.stamp

PDFLATEX_DEFAULT = \
	-pdflatex="pdflatex -file-line-error"
PDFLATEX_NONINTERACTIVE = \
	-pdflatex="pdflatex -file-line-error -interaction=nonstopmode"
BUILD_OPTS = \
	-pdf \
	$(PDFLATEX_DEFAULT) \
	-outdir=$(BUILD_DIR) -cd \
	-out2dir=$(OUT_DIR)

.PHONY: help
help: ## Mostra esta ajuda
	@echo "Uso: make [alvo]"
	@echo ""
	@echo "Alvos disponíveis:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: format
format: ## Formata o código com ruff
	uv run ruff format src
	uv run ruff check --fix src

.PHONY: lint
lint: ## Roda o linter (ruff)
	uv run ruff check src

.PHONY: test
test: ## Roda os testes com pytest
	uv run pytest src/tp2/*.py -v

.PHONY: analise
analise: $(ANALISE_STAMP) ## Gera os graficos da analise em docs/results (usados no relatorio)

$(ANALISE_STAMP): $(SRC_FILES)
	uv run python -m tp2.analise -o $(RESULTS_DIR)
	touch $@

.PHONY: docs
docs: docs-clean analise ## Build-dinamico da documentação/relatorio
	latexmk $(BUILD_OPTS) $(TEX_MAIN) -pvc

.PHONY: docs-build
docs-build: docs-clean analise ## Build final da documentacao/relatorio
	latexmk $(BUILD_OPTS) $(TEX_MAIN)

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
zip: ## Empacota src, pyproject.toml e README.md em um .zip
	rm -f $(ZIP_FILE)
	zip -r $(ZIP_FILE) src pyproject.toml README.md -x '*__pycache__*' -x '*.pyc'
