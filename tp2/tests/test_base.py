"""Leitura das instâncias, h, operadores, orçamento e runner."""

from pathlib import Path

import pytest

from tp2.experimento import Configuracao, carregar, executar, salvar
from tp2.problema import (
    OPERADORES,
    Orcamento,
    OrcamentoEsgotado,
    cronograma,
    guloso,
    h,
    ler_instancia,
)

INSTANCIAS = Path(__file__).parent

# Exemplo com n = 4 e base na origem. A rota (1, 4, 2, 3), de um guloso por proximidade,
# custa 39; o ótimo (1, 4, 3, 2) custa 22.
EXEMPLO = """4
0 0
3 4 2 10 3
6 0 3 14 1
0 8 1 25 2
6 8 4 20 5
"""


@pytest.fixture
def pequena():
    return ler_instancia(INSTANCIAS / "manutencao_pequena.txt")


@pytest.fixture
def exemplo(tmp_path):
    caminho = tmp_path / "exemplo.txt"
    caminho.write_text(EXEMPLO)
    return ler_instancia(caminho)


class TestInstancia:
    @pytest.mark.parametrize(
        ("nome", "n", "soma_p"), [("pequena", 12, 55), ("media", 50, 239), ("grande", 150, 684)]
    )
    def test_leitura(self, nome, n, soma_p):
        inst = ler_instancia(nome)
        assert inst.n == n
        assert sum(inst.p) == soma_p
        assert inst.p[0] == 0

    def test_deslocamentos_exemplo(self, exemplo):
        t = exemplo.t
        assert (t[0][1], t[1][4], t[4][2], t[2][3], t[4][3], t[3][2]) == (5, 5, 8, 10, 6, 10)


class TestFitness:
    def test_identidade_pequena(self, pequena):
        assert h(pequena, list(range(1, 13))) == 4366

    def test_exemplo_cronograma(self, exemplo):
        conclusao, _ = cronograma(exemplo, [1, 4, 2, 3])
        assert conclusao == [7, 16, 27, 38]

    def test_exemplo_guloso_por_proximidade(self, exemplo):
        assert h(exemplo, [1, 4, 2, 3]) == 39

    def test_exemplo_otimo(self, exemplo):
        assert h(exemplo, [1, 4, 3, 2]) == 22

    def test_guloso_pequena(self, pequena):
        # Guloso: escolhe o ativo de menor acréscimo imediato de atraso ponderado;
        # empate (comum no início, quando nada atrasa) vai para o mais próximo.
        # Só esse desempate reproduz 3168 (por índice dá 6935, por prazo 5030).
        perm = guloso(pequena)
        assert perm == [5, 4, 2, 7, 12, 8, 11, 1, 9, 10, 3, 6]
        assert h(pequena, perm) == 3168

    def test_prefixo_nao_decrescente(self, pequena):
        _, custo = cronograma(pequena, list(range(1, 13)))
        assert custo == sorted(custo)


class TestOperadores:
    @pytest.mark.parametrize(
        ("nome", "esperado"),
        [
            ("swap", [3, 2, 1, 5, 7, 8]),
            ("insertion", [3, 1, 5, 2, 7, 8]),
            ("2-opt", [3, 2, 5, 1, 7, 8]),
        ],
    )
    def test_exemplos_operadores(self, nome, esperado):
        assert OPERADORES[nome].aplicar([3, 7, 1, 5, 2, 8], 1, 4) == esperado

    @pytest.mark.parametrize("nome", list(OPERADORES))
    def test_permutacoes_validas(self, nome):
        op, s = OPERADORES[nome], [3, 7, 1, 5, 2, 8, 4, 6]
        for i, j in op.movimentos(len(s)):
            vizinho = op.aplicar(s, i, j)
            assert sorted(vizinho) == sorted(s)
            assert vizinho[: min(i, j)] == s[: min(i, j)]

    @pytest.mark.parametrize("nome", list(OPERADORES))
    @pytest.mark.parametrize("n", [2, 5, 12])
    def test_numero_de_sucessores(self, nome, n):
        op, s = OPERADORES[nome], list(range(1, n + 1))
        vizinhos = [tuple(op.aplicar(s, i, j)) for i, j in op.movimentos(n)]
        assert len(vizinhos) == op.tamanho(n)
        assert len(set(vizinhos)) == len(vizinhos)
        assert tuple(s) not in vizinhos


class TestOrcamento:
    def test_para_exatamente_em_b(self):
        orcamento = Orcamento(10)
        for _ in range(10):
            orcamento.contar(1, [1])
        with pytest.raises(OrcamentoEsgotado):
            orcamento.contar(1, [1])
        assert orcamento.usadas == 10

    def test_historico_registra_cada_melhora(self):
        orcamento = Orcamento(100)
        for valor in [5, 7, 3, 3, 4, 1]:
            orcamento.contar(valor, [valor])
        assert orcamento.historico == [(1, 5), (3, 3), (6, 1)]
        assert (orcamento.melhor_h, orcamento.melhor_s) == (1, [1])


class TestRunner:
    def test_salva_e_rele_csvs(self, tmp_path):
        resultados = [
            executar(Configuracao("tempera", "pequena", e, orcamento=3000)) for e in (0, 1)
        ]
        salvar(resultados, tmp_path)

        execucoes = carregar(tmp_path, "execucoes")
        assert [int(r["execucao"]) for r in execucoes] == [0, 1]
        for r, lido in zip(resultados, execucoes, strict=True):
            assert float(lido["melhor_h"]) == r.melhor_h
            assert int(lido["avaliacoes"]) == r.avaliacoes == 3000
            assert [int(v) for v in lido["melhor_solucao"].split()] == r.melhor_s
            assert float(lido["t0"]) == pytest.approx(r.escalares["t0"])

        historico = carregar(tmp_path, "historico")
        assert len(historico) == sum(len(r.historico) for r in resultados)
        series = carregar(tmp_path, "series")
        assert {r["serie"] for r in series} == {"aceitacao", "temperatura"}

    def test_semente_reproduz_execucao(self):
        config = Configuracao("genetico", "pequena", 3, orcamento=2000)
        assert executar(config).melhor_s == executar(config).melhor_s
