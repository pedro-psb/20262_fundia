"""Simulated annealing."""

import pytest

from tp2.algoritmos.tempera import aceitacao, temperaturas
from tp2.experimento import Configuracao, executar


def test_calibracao_t0_maior_que_tf():
    t0, tf = temperaturas(delta_medio=250.0, p0=0.9, pf=0.001)
    assert t0 > tf > 0
    assert aceitacao(250.0, t0) == pytest.approx(0.9)
    assert aceitacao(250.0, tf) == pytest.approx(0.001)


def test_resfriamento_termina_em_b():
    # 1 avaliação inicial + 200 de calibração + 5 janelas de 1000.
    resultado = executar(Configuracao("tempera", "media", 0, orcamento=5201))
    assert resultado.avaliacoes == 5201
    x, temperatura = resultado.series["temperatura"][-1]
    assert x == 5201
    assert temperatura == pytest.approx(resultado.escalares["tf"])


def test_aceitacao_de_pioras_conforme_temperatura():
    assert aceitacao(100, 1e6) > 0.99
    assert aceitacao(100, 1) < 1e-6


def test_taxa_de_aceitacao_cai_ao_longo_da_execucao():
    resultado = executar(Configuracao("tempera", "media", 0, orcamento=20201))
    taxas = [v for _, v in resultado.series["aceitacao"]]
    assert taxas[0] > 0.5
    assert taxas[-1] < taxas[0] / 4
