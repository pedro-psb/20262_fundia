# TP2

Grupo: Pedro Pessoa, Diogo Muzzi, Paulo Gomes
Disciplina: Fundamentos de Inteligência Artificial

Busca local e algoritmo genético no sequenciamento de manutenção de ativos.

## Divisão de trabalho

Veja [COORDENACAO.md](COORDENACAO.md).

## Reprodução

O enunciado exige instruções exatas para reproduzir cada tabela e figura do relatório. Preencher à medida que as partes ficarem prontas.

| Tabela/Figura | Comando | Resp. |
|---|---|---|
| Verificação de `h` (Seção II) | TODO | Pedro |
| `tab:incremental`, `tab:vizinhancas`, `tab:gd-passos` | TODO | Pedro |
| `tab:sa-parametros`, `fig:sa-aceitacao` | TODO | Paulo |
| `tab:ag-parametros`, `fig:ag-diversidade`, `tab:experimento-ag` | TODO | Diogo |
| `tab:principal`, `fig:boxplots`, `tab:pvalores`, `fig:convergencia`, `tab:tempo` | TODO | Paulo |
| `tab:otimos-locais` | TODO | Pedro |

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

### Rodando a análise

Gera os gráficos no diretório informado por `-o` (padrão: `docs/results`, de onde o relatório os inclui). `make docs` e `make docs-live` rodam a análise antes de compilar o relatório:

```sh
uv run python -m tp2.analise              # salva em docs/results
uv run python -m tp2.analise -o /tmp/out  # outro diretório
```

### Lint

```sh
uv run ruff check .
```

### Relatório

```sh
make docs       # build final em pdf/ (container ghcr.io/xu-cheng/texlive-full, requer docker)
make docs-live  # build contínuo nativo (latexmk -pvc)
```
