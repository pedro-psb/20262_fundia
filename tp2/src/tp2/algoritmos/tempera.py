import math
import random
import statistics

from tp2.problema import Problema, Registro


def aceitacao(delta: float, temperatura: float) -> float:
    """Probabilidade de aceitar uma piora `delta` > 0 (distribuição de Gibbs)."""
    return math.exp(-delta / temperatura)


def temperaturas(delta_medio: float, p0: float, pf: float) -> tuple[float, float]:
    """T0 e Tf tais que uma piora típica é aceita com probabilidade p0 no início e pf no fim."""
    return -delta_medio / math.log(p0), -delta_medio / math.log(pf)


def tempera(
    prob: Problema,
    rng: random.Random,
    reg: Registro,
    p0: float = 0.9,
    pf: float = 0.001,
    amostras: int = 200,
    janela: int = 1000,
) -> None:
    """Simulated annealing com resfriamento geométrico calibrado pela instância.

    A calibração faz um random walk de `amostras` passos (contados no orçamento) para medir
    a piora média; T0 e Tf saem de p0 e pf, e alfa é escolhido para que T chegue a Tf
    exatamente ao fim do orçamento. A taxa de aceitação de pioras é registrada a cada
    `janela` avaliações.
    """
    s = prob.solucao_aleatoria()
    hs = prob.h(s)
    pioras = []
    for _ in range(amostras):
        s2 = prob.sucessor_aleatorio(s)
        h2 = prob.h(s2)
        if h2 > hs:
            pioras.append(h2 - hs)
        s, hs = s2, h2

    delta_medio = statistics.mean(pioras) if pioras else 1.0
    t0, tf = temperaturas(delta_medio, p0, pf)
    alfa = (tf / t0) ** (1 / max(1, prob.restantes()))
    reg.escalares.update(delta_medio=delta_medio, t0=t0, tf=tf, alfa=alfa)

    temperatura = t0
    propostas = aceitas = 0
    avaliacoes = 0
    while True:
        s2 = prob.sucessor_aleatorio(s)
        h2 = prob.h(s2)
        temperatura *= alfa
        avaliacoes += 1
        delta = h2 - hs
        if delta <= 0:
            s, hs = s2, h2
        else:
            propostas += 1
            if rng.random() < aceitacao(delta, temperatura):
                aceitas += 1
                s, hs = s2, h2
        if avaliacoes % janela == 0:
            reg.serie("aceitacao", aceitas / propostas if propostas else 0.0)
            reg.serie("temperatura", temperatura)
            propostas = aceitas = 0
