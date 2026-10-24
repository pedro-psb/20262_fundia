import random
import statistics

from tp2.problema import Problema, Registro

Individuo = tuple[int, list[int]]


def _torneio(populacao: list[Individuo], k: int, rng: random.Random) -> Individuo:
    """Menor h entre k sorteados: só a ordem importa, então não é preciso converter o custo."""
    return min(rng.sample(populacao, k), key=lambda ind: ind[0])


def _registrar(reg: Registro, populacao: list[Individuo], geracao: int) -> None:
    reg.serie("media_populacao", statistics.mean(hi for hi, _ in populacao))
    reg.serie("diversidade", len({tuple(s) for _, s in populacao}), x=geracao)


def genetico(
    prob: Problema,
    rng: random.Random,
    reg: Registro,
    tamanho: int = 100,
    pc: float = 0.9,
    pm: float = 0.2,
    torneio: int = 3,
    elite: int = 2,
) -> None:
    """Algoritmo genético geracional com torneio, OX, mutação e elitismo.

    Filhos idênticos ao pai (sem cruzamento nem mutação) herdam o h do pai sem nova
    avaliação. A diversidade é o número de cromossomos distintos por geração.
    """
    reg.escalares.update(tamanho=tamanho, pc=pc, pm=pm, torneio=torneio, elite=elite, geracoes=0)
    populacao: list[Individuo] = []
    for _ in range(tamanho):
        s = prob.solucao_aleatoria()
        populacao.append((prob.h(s), s))

    geracao = 0
    while True:
        _registrar(reg, populacao, geracao)
        populacao.sort(key=lambda ind: ind[0])
        nova = populacao[:elite]
        while len(nova) < tamanho:
            h_pai, pai = _torneio(populacao, torneio, rng)
            filho = pai
            if rng.random() < pc:
                filho = prob.cruzamento(pai, _torneio(populacao, torneio, rng)[1])
            if rng.random() < pm:
                filho = prob.mutacao(filho)
            nova.append((h_pai if filho is pai else prob.h(filho), filho))
        populacao = nova
        geracao += 1
        reg.escalares["geracoes"] = geracao
