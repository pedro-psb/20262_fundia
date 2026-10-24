"""Operadores sobre permutações: vizinhanças (swap, insertion, 2-opt) e cruzamento OX."""

import random
from collections.abc import Iterator


class Operador:
    """Movimento (i, j) sobre posições 0..n-1; posições antes de min(i, j) não mudam."""

    nome: str

    def tamanho(self, n: int) -> int:
        raise NotImplementedError

    def movimentos(self, n: int) -> Iterator[tuple[int, int]]:
        raise NotImplementedError

    def aplicar(self, s: list[int], i: int, j: int) -> list[int]:
        raise NotImplementedError

    def sortear(self, n: int, rng: random.Random) -> tuple[int, int]:
        i, j = rng.sample(range(n), 2)
        return min(i, j), max(i, j)


class Troca(Operador):
    nome = "swap"

    def tamanho(self, n: int) -> int:
        return n * (n - 1) // 2

    def movimentos(self, n: int) -> Iterator[tuple[int, int]]:
        for i in range(n - 1):
            for j in range(i + 1, n):
                yield i, j

    def aplicar(self, s: list[int], i: int, j: int) -> list[int]:
        novo = list(s)
        novo[i], novo[j] = novo[j], novo[i]
        return novo


class Insercao(Operador):
    """Remove o ativo da posição i e o reinsere na posição j."""

    nome = "insertion"

    def tamanho(self, n: int) -> int:
        return (n - 1) ** 2

    def movimentos(self, n: int) -> Iterator[tuple[int, int]]:
        # (i, i-1) gera o mesmo vizinho que (i-1, i): fica só o segundo.
        for i in range(n):
            for j in range(n):
                if j != i and j != i - 1:
                    yield i, j

    def aplicar(self, s: list[int], i: int, j: int) -> list[int]:
        novo = list(s)
        novo.insert(j, novo.pop(i))
        return novo

    def sortear(self, n: int, rng: random.Random) -> tuple[int, int]:
        while True:
            i, j = rng.sample(range(n), 2)
            if j != i - 1:
                return i, j


class DoisOpt(Operador):
    """Inverte o trecho entre as posições i e j (inclusive)."""

    nome = "2-opt"

    def tamanho(self, n: int) -> int:
        return n * (n - 1) // 2

    def movimentos(self, n: int) -> Iterator[tuple[int, int]]:
        for i in range(n - 1):
            for j in range(i + 1, n):
                yield i, j

    def aplicar(self, s: list[int], i: int, j: int) -> list[int]:
        return s[:i] + s[i : j + 1][::-1] + s[j + 1 :]


OPERADORES: dict[str, Operador] = {op.nome: op for op in (Troca(), Insercao(), DoisOpt())}


def cruzamento_ox(a: list[int], b: list[int], i: int, j: int) -> list[int]:
    """Order Crossover: copia a[i..j] e completa com a ordem de b a partir de j+1, circular."""
    n = len(a)
    filho: list[int | None] = [None] * n
    filho[i : j + 1] = a[i : j + 1]
    herdados = set(a[i : j + 1])
    resto = [b[(j + 1 + k) % n] for k in range(n)]
    posicoes = [(j + 1 + k) % n for k in range(n - (j - i + 1))]
    for pos, gene in zip(posicoes, (g for g in resto if g not in herdados), strict=False):
        filho[pos] = gene
    return [g for g in filho if g is not None]
