"""Algoritmos genéricos: só conhecem a interface `Problema`.

Todo algoritmo tem a assinatura `(prob, rng, reg) -> None` e roda até o orçamento acabar.
"""

import random
from collections.abc import Callable
from functools import partial

from tp2.problema import Problema, Registro

from .aleatoria import busca_aleatoria
from .busca_local import descida
from .genetico import genetico
from .tempera import tempera

Algoritmo = Callable[[Problema, random.Random, Registro], None]

ALGORITMOS: dict[str, Algoritmo] = {
    "aleatoria": busca_aleatoria,
    "gd-best": partial(descida, variante="best"),
    "gd-first": partial(descida, variante="first"),
    "gd-aleatorio": partial(descida, variante="aleatorio"),
    "tempera": tempera,
    "genetico": genetico,
    "genetico-sem-cruzamento": partial(genetico, pc=0.0),
}
