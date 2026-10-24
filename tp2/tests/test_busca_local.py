"""Greedy descent com random restart e avaliação incremental."""

import random

import pytest

from tp2.algoritmos.busca_local import VARIANTES, descer
from tp2.experimento import Configuracao, executar
from tp2.problema import OPERADORES, Manutencao, Orcamento, Solucao, h, ler_instancia


@pytest.mark.parametrize("variante", ["best", "first"])
@pytest.mark.parametrize("operador", list(OPERADORES))
def test_descida_termina_em_otimo_local(variante, operador):
    inst = ler_instancia("pequena")
    prob = Manutencao(inst, Orcamento(10**7), random.Random(0), operador)
    s = prob.solucao_aleatoria()
    s, hs = descer(prob, s, prob.h(s), variante)
    assert hs == h(inst, s)
    assert all(h(inst, vizinho) >= hs for vizinho in prob.sucessores(s))


@pytest.mark.parametrize("variante", list(VARIANTES))
def test_variantes_respeitam_orcamento(variante):
    resultado = executar(Configuracao(f"gd-{variante}", "media", 0, orcamento=1234))
    assert resultado.avaliacoes == 1234


@pytest.mark.parametrize("operador", list(OPERADORES))
def test_incremental_igual_completa(operador):
    inst = ler_instancia("grande")
    rng = random.Random(1)
    prob = Manutencao(inst, Orcamento(10**7), rng, operador, incremental=True)
    s = prob.solucao_aleatoria()
    hs = prob.h(s)
    for _ in range(2000):
        s2 = prob.sucessor_aleatorio(s)
        h2 = prob.h(s2)
        assert h2 == h(inst, list(s2))
        if h2 <= hs or rng.random() < 0.3:
            s, hs = s2, h2
    mutante = prob.mutacao(s)
    assert prob.h(mutante) == h(inst, list(mutante))


def test_incremental_aproveita_o_pai():
    inst = ler_instancia("pequena")
    prob = Manutencao(inst, Orcamento(100), random.Random(0))
    s = Solucao(list(range(1, 13)))
    prob.h(s)
    vizinho = next(prob.sucessores(s))
    assert vizinho.pai is s
    prob.h(vizinho)
    assert s.conclusao is not None
