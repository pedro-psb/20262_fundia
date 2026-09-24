import heapq
import itertools
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass

import pytest

from ponte_tocha.base import EspacoEstado, Estado, Movimento, Pessoa, Sucessor, h_max_origem


@dataclass(frozen=True)
class ResultadoBusca:
    """Resultado de uma busca no espaço de estados."""

    caminho: list[Estado]
    custo_caminho: int
    nos_visitados: int
    tempo_processamento: float


class Busca(ABC):
    def __init__(self, espaco_estado: EspacoEstado):
        self._espaco_estado = espaco_estado

    @abstractmethod
    def buscar(self) -> ResultadoBusca | None:
        """Executa a busca e retorna o resultado.

        Retorna None se não houver solução.
        """


class BuscaEmLargura(Busca):
    def buscar(self, limite_nos: int | None = None) -> ResultadoBusca | None:
        inicio_tempo = time.perf_counter()
        estado_inicial = self._espaco_estado.estado_inicial

        chave_inicial = (
            estado_inicial.origem,
            estado_inicial.destino,
            estado_inicial.tocha_na_origem,
        )

        fila: deque[tuple[Estado, list[Estado], int]] = deque(
            [(estado_inicial, [estado_inicial], 0)]
        )
        visitados = {chave_inicial}
        nos_visitados = 0

        while fila:
            if limite_nos is not None and nos_visitados >= limite_nos:
                return None

            estado_atual, caminho, custo_atual = fila.popleft()
            nos_visitados += 1

            if estado_atual.is_estado_final():
                fim_tempo = time.perf_counter()
                return ResultadoBusca(
                    caminho=caminho,
                    custo_caminho=custo_atual,
                    nos_visitados=nos_visitados,
                    tempo_processamento=fim_tempo - inicio_tempo,
                )

            for sucessor in self._espaco_estado.fn_sucessora(estado_atual):
                chave_sucessor = (
                    sucessor.estado.origem,
                    sucessor.estado.destino,
                    sucessor.estado.tocha_na_origem,
                )
                if chave_sucessor not in visitados:
                    visitados.add(chave_sucessor)
                    fila.append(
                        (
                            sucessor.estado,
                            caminho + [sucessor.estado],
                            custo_atual + sucessor.custo,
                        )
                    )

        return None


class BuscaEmProfundidade(Busca):
    def buscar(self, limite_nos: int | None = None) -> ResultadoBusca | None:
        inicio_tempo = time.perf_counter()
        estado_inicial = self._espaco_estado.estado_inicial

        pilha: list[tuple[Estado, list[Estado], int]] = [(estado_inicial, [estado_inicial], 0)]
        visitados: set[tuple[frozenset[Pessoa], frozenset[Pessoa], bool]] = set()
        nos_visitados = 0

        while pilha:
            if limite_nos is not None and nos_visitados >= limite_nos:
                return None

            estado_atual, caminho, custo_atual = pilha.pop()

            chave_atual = (
                estado_atual.origem,
                estado_atual.destino,
                estado_atual.tocha_na_origem,
            )
            if chave_atual in visitados:
                continue

            visitados.add(chave_atual)
            nos_visitados += 1

            if estado_atual.is_estado_final():
                fim_tempo = time.perf_counter()
                return ResultadoBusca(
                    caminho=caminho,
                    custo_caminho=custo_atual,
                    nos_visitados=nos_visitados,
                    tempo_processamento=fim_tempo - inicio_tempo,
                )

            for sucessor in self._espaco_estado.fn_sucessora(estado_atual):
                chave_sucessor = (
                    sucessor.estado.origem,
                    sucessor.estado.destino,
                    sucessor.estado.tocha_na_origem,
                )
                if chave_sucessor not in visitados:
                    pilha.append(
                        (
                            sucessor.estado,
                            caminho + [sucessor.estado],
                            custo_atual + sucessor.custo,
                        )
                    )

        return None


class BuscaDeCustoUniforme(Busca):
    def buscar(self) -> ResultadoBusca | None:
        inicio_tempo = time.perf_counter()

        estado_inicial = self._espaco_estado.estado_inicial

        contador = itertools.count()

        fronteira = [(0, next(contador), estado_inicial, [estado_inicial])]

        # A heurística não faz parte da identidade lógica do estado.
        chave_inicial = (
            estado_inicial.origem,
            estado_inicial.destino,
            estado_inicial.tocha_na_origem,
        )
        melhor_custo = {chave_inicial: 0}

        nos_visitados = 0

        while fronteira:
            custo_atual, _, estado_atual, caminho = heapq.heappop(fronteira)
            chave_atual = (
                estado_atual.origem,
                estado_atual.destino,
                estado_atual.tocha_na_origem,
            )

            if custo_atual != melhor_custo.get(chave_atual):
                continue

            nos_visitados += 1

            if estado_atual.is_estado_final():
                fim_tempo = time.perf_counter()

                return ResultadoBusca(
                    caminho=caminho,
                    custo_caminho=custo_atual,
                    nos_visitados=nos_visitados,
                    tempo_processamento=fim_tempo - inicio_tempo,
                )

            sucessores = self._espaco_estado.fn_sucessora(estado_atual)

            for sucessor in sucessores:
                novo_custo = custo_atual + sucessor.custo
                chave_sucessor = (
                    sucessor.estado.origem,
                    sucessor.estado.destino,
                    sucessor.estado.tocha_na_origem,
                )

                custo_conhecido = melhor_custo.get(
                    chave_sucessor,
                    float("inf"),
                )

                if novo_custo < custo_conhecido:
                    melhor_custo[chave_sucessor] = novo_custo

                    heapq.heappush(
                        fronteira,
                        (
                            novo_custo,
                            next(contador),
                            sucessor.estado,
                            caminho + [sucessor.estado],
                        ),
                    )

        return None


class BuscaAEstrela(Busca):
    def buscar(self) -> ResultadoBusca | None:
        inicio_tempo = time.perf_counter()
        estado_inicial = self._espaco_estado.estado_inicial
        contador = itertools.count()

        fronteira = [
            (
                estado_inicial.estimativa_heuristica,
                next(contador),
                0,
                estado_inicial,
                [estado_inicial],
            )
        ]
        # A heurística não faz parte da identidade lógica do estado.
        chave_inicial = (
            estado_inicial.origem,
            estado_inicial.destino,
            estado_inicial.tocha_na_origem,
        )
        melhor_custo = {chave_inicial: 0}
        nos_visitados = 0

        while fronteira:
            _, _, custo_atual, estado_atual, caminho = heapq.heappop(fronteira)
            chave_atual = (
                estado_atual.origem,
                estado_atual.destino,
                estado_atual.tocha_na_origem,
            )
            if custo_atual != melhor_custo.get(chave_atual):
                continue

            # Mesma métrica da UCS: retiradas válidas, incluindo o objetivo.
            nos_visitados += 1
            if estado_atual.is_estado_final():
                return ResultadoBusca(
                    caminho=caminho,
                    custo_caminho=custo_atual,
                    nos_visitados=nos_visitados,
                    tempo_processamento=time.perf_counter() - inicio_tempo,
                )

            for sucessor in self._espaco_estado.fn_sucessora(estado_atual):
                novo_custo = custo_atual + sucessor.custo
                chave_sucessor = (
                    sucessor.estado.origem,
                    sucessor.estado.destino,
                    sucessor.estado.tocha_na_origem,
                )
                if novo_custo < melhor_custo.get(chave_sucessor, float("inf")):
                    melhor_custo[chave_sucessor] = novo_custo
                    prioridade = novo_custo + sucessor.estado.estimativa_heuristica
                    heapq.heappush(
                        fronteira,
                        (
                            prioridade,
                            next(contador),
                            novo_custo,
                            sucessor.estado,
                            caminho + [sucessor.estado],
                        ),
                    )

        return None


# Testes

CUSTOS_INICIAIS = [1, 2, 5]
CASOS_CUSTO_OTIMO = [
    ([1], 1),
    ([1, 2], 2),
    ([1, 2, 5], 8),
    ([1, 2, 5, 10], 17),
    ([2, 2, 2], 6),
]


class TestBuscas:
    @pytest.mark.parametrize("custos", [[1], [1, 2], [1, 2, 5], [1, 2, 5, 10]])
    def test_busca_em_largura(self, custos):
        espaco_estado = EspacoEstado(Pessoa.factory(custos))
        busca = BuscaEmLargura(espaco_estado)
        resultado = busca.buscar()

        assert resultado is not None
        assert resultado.nos_visitados > 0
        self._verificar_caminho(espaco_estado, resultado)

    @pytest.mark.parametrize("custos", [[1], [1, 2], [1, 2, 5], [1, 2, 5, 10]])
    def test_busca_em_profundidade(self, custos):
        espaco_estado = EspacoEstado(Pessoa.factory(custos))
        busca = BuscaEmProfundidade(espaco_estado)
        resultado = busca.buscar()

        assert resultado is not None
        assert resultado.nos_visitados > 0
        self._verificar_caminho(espaco_estado, resultado)

    def test_busca_com_limite_nos(self):
        espaco_estado = EspacoEstado(Pessoa.factory([1, 2, 5, 10]))
        assert BuscaEmLargura(espaco_estado).buscar(limite_nos=1) is None
        assert BuscaEmProfundidade(espaco_estado).buscar(limite_nos=1) is None

    @pytest.mark.parametrize("custos, custo_esperado", CASOS_CUSTO_OTIMO)
    def test_busca_de_custo_uniforme(self, custos, custo_esperado):
        espaco_estado = EspacoEstado(Pessoa.factory(custos))
        busca = BuscaDeCustoUniforme(espaco_estado)

        resultado = busca.buscar()

        assert resultado is not None
        assert resultado.custo_caminho == custo_esperado
        self._verificar_caminho(espaco_estado, resultado)

    @pytest.mark.parametrize("custos, custo_esperado", CASOS_CUSTO_OTIMO)
    def test_busca_a_estrela(self, custos, custo_esperado):
        espaco_estado = EspacoEstado(Pessoa.factory(custos), fn_heuristica=h_max_origem)
        busca = BuscaAEstrela(espaco_estado)

        resultado = busca.buscar()
        resultado_ucs = BuscaDeCustoUniforme(espaco_estado).buscar()

        assert resultado is not None
        assert resultado_ucs is not None
        assert resultado.custo_caminho == resultado_ucs.custo_caminho == custo_esperado
        self._verificar_caminho(espaco_estado, resultado)
        self._verificar_caminho(espaco_estado, resultado_ucs)

    @pytest.mark.parametrize("custos, custo_esperado", CASOS_CUSTO_OTIMO)
    def test_busca_a_estrela_com_heuristica_zero(self, custos, custo_esperado):
        espaco_estado = EspacoEstado(Pessoa.factory(custos))
        resultado = BuscaAEstrela(espaco_estado).buscar()
        resultado_ucs = BuscaDeCustoUniforme(espaco_estado).buscar()

        assert resultado is not None
        assert resultado_ucs is not None
        assert resultado.custo_caminho == resultado_ucs.custo_caminho == custo_esperado
        self._verificar_caminho(espaco_estado, resultado)

    @pytest.mark.parametrize("heuristica_b, expansoes_a", [(0, 1), (5, 2)])
    def test_busca_a_estrela_reconsidera_caminho_melhor(
        self, monkeypatch, heuristica_b, expansoes_a
    ):
        p1, p2 = Pessoa(1), Pessoa(2)
        espaco_estado = EspacoEstado([p1, p2], fn_heuristica=h_max_origem)
        inicial = espaco_estado.estado_inicial
        estado_a = Estado.new({p1}, {p2}, False, 0)
        estado_b = Estado.new({p2}, {p1}, False, heuristica_b)
        objetivo = espaco_estado.estado_objetivo

        # Grafo controlado: inicial -> A custa 3; inicial -> B -> A custa 2.
        # Com h(B)=0, a entrada antiga de A deve ser descartada.
        # Com h(B)=5 (admissível, inconsistente), A precisa ser expandido de novo.
        grafo = {
            inicial: [Sucessor(estado_a, Movimento.IR, 3), Sucessor(estado_b, Movimento.IR, 1)],
            estado_b: [Sucessor(estado_a, Movimento.VOLTAR, 1)],
            estado_a: [Sucessor(objetivo, Movimento.IR, 4)],
        }
        expandidos = []

        def sucessores_teste(estado):
            expandidos.append(estado)
            return grafo.get(estado, [])

        monkeypatch.setattr(espaco_estado, "fn_sucessora", sucessores_teste)
        resultado = BuscaAEstrela(espaco_estado).buscar()

        assert resultado is not None
        assert resultado.custo_caminho == 6
        assert resultado.caminho == [inicial, estado_b, estado_a, objetivo]
        assert expandidos.count(estado_a) == expansoes_a
        assert resultado.nos_visitados == len(expandidos) + 1

    def _verificar_caminho(self, espaco_estado, resultado):
        assert resultado.caminho[0] == espaco_estado.estado_inicial
        assert resultado.caminho[-1] == espaco_estado.estado_objetivo
        custo_total = 0

        for atual, proximo in zip(resultado.caminho, resultado.caminho[1:], strict=False):
            assert proximo.tocha_na_origem != atual.tocha_na_origem
            if atual.tocha_na_origem:
                pessoas_movidas = atual.origem - proximo.origem
                assert proximo.origem == atual.origem - pessoas_movidas
                assert proximo.destino == atual.destino | pessoas_movidas
            else:
                pessoas_movidas = atual.destino - proximo.destino
                assert proximo.destino == atual.destino - pessoas_movidas
                assert proximo.origem == atual.origem | pessoas_movidas

            assert 1 <= len(pessoas_movidas) <= 2
            custo_total += max(p.custo for p in pessoas_movidas)

        assert custo_total == resultado.custo_caminho
