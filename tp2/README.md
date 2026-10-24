# TP2

Grupo: Pedro Pessoa, Diogo Muzzi, Paulo Gomes
Disciplina: Fundamentos de Inteligência Artificial

Busca local e algoritmo genético no sequenciamento de manutenção de ativos.

## Reprodução

O enunciado exige instruções exatas para reproduzir cada tabela e figura do relatório. Os CSVs brutos vão para `docs/results/raw/` e as tabelas e figuras finais, incluídas no relatório, vão para `docs/results/final/`.

```sh
# Verificação de h (Seção II): saída do terminal
make verificar

# tab:incremental      docs/results/final/tab-incremental.tex
# tab:vizinhancas      docs/results/final/tab-vizinhancas.tex
# tab:gd-passos        docs/results/final/tab-gd-passos.tex
# tab:otimos-locais    docs/results/final/tab-otimos-locais.tex
make resultado-local analise

# tab:sa-parametros    docs/results/final/tab-sa-parametros.tex
# fig:sa-aceitacao     docs/results/final/sa_aceitacao.png
make resultado-tempera analise

# tab:ag-parametros    docs/results/final/tab-ag-parametros.tex
# tab:experimento-ag   docs/results/final/tab-experimento-ag.tex
# fig:ag-diversidade   docs/results/final/ag_diversidade.png
make resultado-genetico analise

# tab:principal        docs/results/final/tab-principal.tex
# tab:tempo            docs/results/final/tab-tempo.tex
# tab:pvalores         docs/results/final/tab-pvalores.tex
# fig:boxplots         docs/results/final/boxplots.png
# fig:convergencia     docs/results/final/convergencia.png
make resultado-todos analise
```

## Contribuindo

### Setup

Com [uv](https://docs.astral.sh/uv/) (recomendado):

```sh
uv sync
```

Ou com `venv` + `pip`:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest ruff
```

### Rodando os testes

Os testes ficam em `tests/` (um arquivo por parte, ver [COORDENACAO.md](COORDENACAO.md)), junto com as instâncias `manutencao_*.txt`:

```sh
make test
uv run pytest tests/test_base.py          # um arquivo
uv run pytest tests -s                    # mostra resultado de prints!
uv run pytest tests -k palavra            # filtra por testes que tenham 'palavra'
```

### Rodando os experimentos

```sh
uv run tp2 run verificar                          # valores de verificação de h
uv run tp2 run tempera                            # todas as instâncias → docs/results/raw
uv run tp2 run tempera -i pequena                 # uma instância (nome ou caminho)
uv run tp2 run gd-first --operador 2-opt          # outra vizinhança
uv run tp2 run genetico --execucoes 3 --orcamento 5000   # rodada rápida
uv run tp2 run incremental                        # tempo completa × incremental
uv run tp2 run --help                             # algoritmos e opções
make resultado-todos RUN_ARGS="--execucoes 2 --orcamento 3000"   # rodada rápida, para testar
```

### Tratando os resultados

Lê os CSVs brutos (padrão: `docs/results/raw`) e gera em `-o` (padrão: `docs/results/final`, de onde o relatório os inclui) as linhas de cada tabela (`tab-*.tex`), as figuras e os resumos `resumo.csv` e `pvalores.csv`. Sem dados, as tabelas saem com "--" e o relatório compila mesmo assim. `make docs` e `make docs-live` rodam este passo antes de compilar o relatório:

```sh
uv run tp2 tratar-resultados
uv run tp2 tratar-resultados outros/csvs -o /tmp/out
```

### Lint

```sh
make lint
```

### Relatório

```sh
make docs       # build final em pdf/ (container ghcr.io/xu-cheng/texlive-full, requer docker)
make docs-live  # build contínuo nativo (latexmk -pvc)
```
