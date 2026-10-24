"""Algoritmo genético."""

import random

from tp2.experimento import Configuracao, executar
from tp2.problema import Manutencao, Orcamento, cruzamento_ox, ler_instancia


def test_cruzamento_e_mutacao_validos():
    inst = ler_instancia("grande")
    prob = Manutencao(inst, Orcamento(1), random.Random(0))
    esperado = list(range(1, inst.n + 1))
    for _ in range(200):
        a, b = prob.solucao_aleatoria(), prob.solucao_aleatoria()
        assert sorted(prob.cruzamento(a, b)) == esperado
        assert sorted(prob.mutacao(a)) == esperado


def test_exemplo_de_cruzamento_do_relatorio():
    # Exemplo de Eiben & Smith: segmento 4 5 6 7 (posições 3..6) herdado do pai 1;
    # o resto vem do pai 2 na ordem 1 9 3 8 2, a partir da posição 7, circular.
    pai1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    pai2 = [9, 3, 7, 8, 2, 6, 5, 1, 4]
    assert cruzamento_ox(pai1, pai2, 3, 6) == [3, 8, 2, 4, 5, 6, 7, 1, 9]


def test_orcamento_com_ultima_geracao_incompleta():
    resultado = executar(Configuracao("genetico", "media", 0, orcamento=100 + 37))
    assert resultado.avaliacoes == 137


def test_registra_diversidade_e_media_da_populacao():
    resultado = executar(Configuracao("genetico", "pequena", 0, orcamento=5000))
    diversidade = [v for _, v in resultado.series["diversidade"]]
    assert diversidade[0] == 100
    assert len(resultado.series["media_populacao"]) == len(diversidade)
