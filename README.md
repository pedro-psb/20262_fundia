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

Os testes ficam dentro do próprio arquivo de implementação (ex.: `src/ponte_tocha/base.py`). Rode apontando para o arquivo:

```sh
uv run pytest src/ponte_tocha/base.py
uv run pytest src/ponte_tocha/base.py -s          # mostra resultado de prints!
uv run pytest src/ponte_tocha/base.py -k palavra  # filtra por testes que tenha 'palavar'
```

### Rodando a análise

Roda cada algoritmo de busca contra um problema fixo em repetidas iterações (por padrão, 100 repetições) calculando as médias e salvando um CSV e um gráfico comparando-os (custo do caminho, nós visitados e tempo) no diretório informado:

```sh
uv run python -m ponte_tocha.analise results
uv run python -m ponte_tocha.analise results --repeticoes 500  # altera o número de repetições
```

### Lint

```sh
uv run ruff check .
```
