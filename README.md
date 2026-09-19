# TP1: Ponte e tocha

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

### Rodando os testes

Os testes ficam dentro do próprio arquivo de implementação (ex.: `src/ponte_tocha/main.py`). Rode apontando para o arquivo:

```sh
uv run pytest src/ponte_tocha/main.py
```

### Lint

```sh
uv run ruff check .
```
