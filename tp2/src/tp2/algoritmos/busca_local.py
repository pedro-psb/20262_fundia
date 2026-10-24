import random
from collections.abc import Callable

from tp2.problema import Problema, Registro

Passo = Callable[[Problema, list[int], int, int], tuple[list[int], int] | None]


def _melhor_melhora(prob, s, hs, paciencia):
    melhor = None
    for s2 in prob.sucessores(s):
        h2 = prob.h(s2)
        if h2 < hs and (melhor is None or h2 < melhor[1]):
            melhor = (s2, h2)
    return melhor


def _primeira_melhora(prob, s, hs, paciencia):
    for s2 in prob.sucessores(s):
        h2 = prob.h(s2)
        if h2 < hs:
            return s2, h2
    return None


def _melhora_aleatoria(prob, s, hs, paciencia):
    for _ in range(paciencia):
        s2 = prob.sucessor_aleatorio(s)
        h2 = prob.h(s2)
        if h2 < hs:
            return s2, h2
    return None


VARIANTES: dict[str, Passo] = {
    "best": _melhor_melhora,
    "first": _primeira_melhora,
    "aleatorio": _melhora_aleatoria,
}


def descer(
    prob: Problema,
    s: list[int],
    hs: int,
    variante: str = "best",
    paciencia: int = 0,
    reg: Registro | None = None,
) -> tuple[list[int], int]:
    """Uma descida a partir de s, até nenhum passo da variante melhorar h."""
    passo = VARIANTES[variante]
    while (proximo := passo(prob, s, hs, paciencia)) is not None:
        s, hs = proximo
        if reg is not None:
            reg.somar("passos")
    return s, hs


def descida(
    prob: Problema,
    rng: random.Random,
    reg: Registro,
    variante: str = "best",
    paciencia: int | None = None,
) -> None:
    """Greedy descent com random restart.

    Na variante 'aleatorio' não há varredura completa da vizinhança: a descida para após
    `paciencia` sorteios seguidos sem melhora (por padrão, o tamanho da vizinhança), e o
    ponto final não é necessariamente um ótimo local.
    """
    if paciencia is None:
        paciencia = prob.tamanho_vizinhanca()
    otimos: set[tuple[int, ...]] = set()
    reg.escalares.update(passos=0, restarts=0)
    primeira = True
    while True:
        if not primeira:
            reg.somar("restarts")
        primeira = False
        s = prob.solucao_aleatoria()
        s, _ = descer(prob, s, prob.h(s), variante, paciencia, reg)
        if variante != "aleatorio":
            otimos.add(tuple(s))
            reg.escalares["otimos_distintos"] = len(otimos)
