"""Leitura das instâncias, h, operadores, orçamento e runner."""

from pathlib import Path

import pytest

from tp2.problema import guloso, h, ler_instancia

INSTANCIAS = Path(__file__).parent

# Exemplo da Fig. 1 do enunciado. As coordenadas não vêm no texto: foram lidas do
# desenho e conferidas com o cronograma (C = 7, 16, 27, 38).
FIG1 = """4
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
def fig1(tmp_path):
    caminho = tmp_path / "fig1.txt"
    caminho.write_text(FIG1)
    return ler_instancia(caminho)


class TestFitness:
    def test_identidade_pequena(self, pequena):
        assert h(pequena, list(range(1, 13))) == 4366

    def test_fig1_guloso_por_proximidade(self, fig1):
        assert h(fig1, [1, 4, 2, 3]) == 39

    def test_fig1_otimo(self, fig1):
        assert h(fig1, [1, 4, 3, 2]) == 22

    def test_guloso_pequena(self, pequena):
        # Guloso: escolhe o ativo de menor acréscimo imediato de atraso ponderado;
        # empate (comum no início, quando nada atrasa) vai para o mais próximo.
        # Só esse desempate reproduz 3168 (por índice dá 6935, por prazo 5030).
        perm = guloso(pequena)
        assert perm == [5, 4, 2, 7, 12, 8, 11, 1, 9, 10, 3, 6]
        assert h(pequena, perm) == 3168


class TestOperadores:
    @pytest.mark.skip(reason="não implementado")
    def test_permutacoes_validas(self):
        """Para swap, insertion e 2-opt, todo sucessor é permutação de 1..n."""

    @pytest.mark.skip(reason="não implementado")
    def test_numero_de_sucessores(self):
        """Cada operador gera o tamanho de vizinhança esperado em função de n."""


class TestOrcamento:
    @pytest.mark.skip(reason="não implementado")
    def test_para_exatamente_em_b(self):
        """O contador de avaliações para exatamente em B, nem antes nem depois."""

    @pytest.mark.skip(reason="não implementado")
    def test_historico_registra_cada_melhora(self):
        """O histórico (melhor h × avaliações) ganha uma entrada a cada melhora."""


class TestRunner:
    @pytest.mark.skip(reason="não implementado")
    def test_salva_e_rele_csvs(self, tmp_path):
        """O runner grava <algoritmo>_execucoes.csv e _historico.csv e os relê iguais."""
