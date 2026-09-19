from abc import ABC, abstractmethod
from dataclasses import dataclass

from ponte_tocha.base import EspacoEstado, Estado, Pessoa


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
        self._visitados: set[Estado] = set()  # para evitar ciclos

    @abstractmethod
    def buscar(self) -> ResultadoBusca | None:
        """Executa a busca e retorna o resultado.

        Retorna None se não houver solução.
        """


class BuscaEmLargura(Busca):
    def buscar(self) -> ResultadoBusca | None: ...


class BuscaEmProfundidade(Busca):
    def buscar(self) -> ResultadoBusca | None: ...


class BuscaDeCustoUniforme(Busca):
    def buscar(self) -> ResultadoBusca | None: ...


class BuscaAEstrela(Busca):
    def buscar(self) -> ResultadoBusca | None: ...


# Testes

CUSTOS_INICIAIS = [1, 2, 5]


class TestBuscas:
    def test_busca_em_largura(self):
        espaco_estado = EspacoEstado(Pessoa.factory(CUSTOS_INICIAIS))
        busca = BuscaEmLargura(espaco_estado)
        # TODO: calcular resposta esperada na mao
        esperado = None
        assert busca.buscar() == esperado

    def test_busca_em_profundidade(self):
        espaco_estado = EspacoEstado(Pessoa.factory(CUSTOS_INICIAIS))
        busca = BuscaEmProfundidade(espaco_estado)
        # TODO: calcular resposta esperada na mao
        esperado = None
        assert busca.buscar() == esperado

    def test_busca_de_custo_uniforme(self):
        espaco_estado = EspacoEstado(Pessoa.factory(CUSTOS_INICIAIS))
        busca = BuscaDeCustoUniforme(espaco_estado)
        # TODO: calcular resposta esperada na mao
        esperado = None
        assert busca.buscar() == esperado

    def test_busca_a_estrela(self):
        espaco_estado = EspacoEstado(Pessoa.factory(CUSTOS_INICIAIS))
        busca = BuscaAEstrela(espaco_estado)
        # TODO: calcular resposta esperada na mao
        esperado = None
        assert busca.buscar() == esperado
