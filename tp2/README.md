# TP2

Grupo: Pedro Pessoa, Diogo Muzzi, Paulo Gomes
Disciplina: Fundamentos de Inteligência Artificial

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

### Rodando

```sh
uv run python -m tp2.main
```

### Rodando os testes

Os testes ficam dentro do próprio arquivo de implementação (ex.: `src/tp2/main.py`). Rode apontando para o arquivo:

```sh
uv run pytest src/tp2/main.py
uv run pytest src/tp2/main.py -s          # mostra resultado de prints!
uv run pytest src/tp2/main.py -k palavra  # filtra por testes que tenham 'palavra'
```

### Rodando a análise

Gera os gráficos no diretório informado por `-o` (padrão: `docs/results`, de onde o relatório os inclui). `make docs` e `make docs-build` rodam a análise antes de compilar o relatório:

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
make docs        # build contínuo (latexmk -pvc)
make docs-build  # build final em pdf/
```
