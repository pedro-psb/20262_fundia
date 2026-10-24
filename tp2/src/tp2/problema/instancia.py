"""Leitura das instâncias e valores de referência."""

import math
from dataclasses import dataclass
from pathlib import Path

DIRETORIO_INSTANCIAS = Path(__file__).resolve().parents[3] / "tests"
NOMES_INSTANCIAS = ("pequena", "media", "grande")
REFERENCIAS = {"pequena": 1875, "media": 16332, "grande": 60417}


@dataclass(frozen=True)
class Instancia:
    """Dados de uma instância; o índice 0 é a base (p[0] = 0)."""

    nome: str
    p: list[int]
    d: list[int]
    w: list[int]
    t: list[list[int]]

    @property
    def n(self) -> int:
        return len(self.p) - 1


def caminho_instancia(origem: str | Path) -> Path:
    """Aceita o nome curto ('pequena', 'media', 'grande') ou um caminho."""
    if str(origem) in NOMES_INSTANCIAS:
        return DIRETORIO_INSTANCIAS / f"manutencao_{origem}.txt"
    return Path(origem)


def ler_instancia(origem: str | Path) -> Instancia:
    caminho = caminho_instancia(origem)
    valores = [int(v) for v in caminho.read_text().split()]
    n = valores[0]
    x, y = [valores[1]], [valores[2]]
    p, d, w = [0], [0], [0]
    for j in range(n):
        xj, yj, pj, dj, wj = valores[3 + 5 * j : 8 + 5 * j]
        x.append(xj)
        y.append(yj)
        p.append(pj)
        d.append(dj)
        w.append(wj)
    # Com coordenadas inteiras a distância nunca cai exatamente em .5, então o
    # arredondamento do Python (para o par mais próximo) equivale ao usual.
    t = [[round(math.hypot(x[i] - x[j], y[i] - y[j])) for j in range(n + 1)] for i in range(n + 1)]
    nome = caminho.stem.removeprefix("manutencao_")
    return Instancia(nome, p, d, w, t)
