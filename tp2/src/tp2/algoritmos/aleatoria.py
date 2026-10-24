import random

from tp2.problema import Problema, Registro


def busca_aleatoria(prob: Problema, rng: random.Random, reg: Registro) -> None:
    """Amostra permutações aleatórias até esgotar o orçamento (algoritmo de referência)."""
    while True:
        prob.h(prob.solucao_aleatoria())
