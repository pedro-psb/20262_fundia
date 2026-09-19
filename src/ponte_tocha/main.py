from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from pprint import pprint
from typing import NamedTuple

counter = 0


def get_id() -> int:
    global counter
    id = counter
    counter += 1
    return id


@dataclass(frozen=True)
class Pessoa:
    """
    A representação de uma pessoa.

    Args:
        id: Identificador único de uma pessoa.
        custo: O custo (em minutos) de travessia dessa pessoa
    """

    custo: int
    id: int = field(default_factory=get_id)

    def __repr__(self) -> str:
        """Representacao compacta para debugging."""
        return f"p_{self.id}(c={self.custo})"


class Estado(NamedTuple):
    """
    Representa um estado no problema da ponte e tocha.

    Args:
        origem: Representa o conjunto de pessoas do lado inicial da ponte.
        destino: Representa o conjunto de pessoas no lado final da ponte.
        tocha_na_origem: Verdadeira se a tocha está atualmente no lado inicial da ponte.
        estimativa_heuristica: O valor estimado para a heuristica
    """

    origem: frozenset[Pessoa]
    destino: frozenset[Pessoa]
    tocha_na_origem: bool
    estimativa_heuristica: int = 0

    @classmethod
    def init(cls, custos_iniciais: Sequence[int]) -> "Estado":
        pessoas_origem = set()
        for custo in custos_iniciais:
            pessoas_origem.add(Pessoa(custo))
        return cls(frozenset(pessoas_origem), frozenset(), True)

    def is_estado_final(self) -> bool:
        origem_vazia = len(self.origem) == 0
        destino_nao_vazio = len(self.destino) != 0
        tocha_no_destino = not self.tocha_na_origem
        return origem_vazia and destino_nao_vazio and tocha_no_destino

    def is_estado_inicial(self) -> bool:
        origem_nao_vazia = len(self.origem) != 0
        destino_vazio = len(self.destino) == 0
        return origem_nao_vazia and destino_vazio and self.tocha_na_origem

    def get_candidatos(self) -> set[frozenset[Pessoa] | frozenset[Pessoa, Pessoa]]:
        """
        Retorna a lista de candidatos a atravessar a ponte.

        Um ou duas pessoas podem atravessar a ponte ao mesmo tempo.

        Exemplo:
            >>> estado = Estado({1,2,3}, {})
            >>> estado.get_candidatos()
            [{1}, {2}, {3}, {1,2}, {2,3}, {1,3}]
        """
        combinacoes = set()
        for p_i in self.origem:
            combinacoes.add(frozenset((p_i,)))
            for p_j in self.origem:
                combinacoes.add(frozenset((p_i, p_j)))
        return combinacoes

    def __repr__(self) -> str:
        """Representacao compacta para debugging."""
        compacto = (
            self.origem,
            self.destino,
            self.tocha_na_origem,
            self.estimativa_heuristica,
        )
        return str(compacto)


class Acoes(StrEnum):
    ir = "ir"
    voltar = "voltar"


@dataclass(frozen=True)
class EstadoDestino:
    """Representa o destino em um mapa de adjacência.

    Encapsula propriedades da aresta como a acao e o peso.
    """

    estado: Estado
    acao: Acoes
    custo: int = 0


class EspacoEstado:
    def __init__(self, pessoas: Sequence[Pessoa], fn_heuristica=None):
        self._estado_inicial = Estado(frozenset(pessoas), frozenset(), True, 0)
        # Mapa de Adjacencia:
        # 
        # Mapeia um nó para os vizinhos (directionados) com um peso associado.
        # Exemplos, dados os estados e0, e1 e e2:
        #
        # a) e0 tem uma aresta para e1 e para e2, sem custos
        # e0: { EstadoDestino(e1, "ir"), EstadoDestino(e2, "voltar") }
        #
        # b) item, mas com custos associados
        # e0: { EstadoDestino(e1, "ir", custo=1), EstadoDestino(e2, "voltar", custo=2) }
        self._mapa_adjacencia: dict[Estado, frozenset(EstadoDestino, ...)] = {
            self._estado_inicial: self.fn_sucessora(self._estado_inicial)
        }
        self._fn_heuristica = fn_heuristica or h_padrao
        self._pessoas = pessoas

    @property
    def estado_inicial(self) -> Estado:
        """Retorna o estado inicial."""
        return self._estado_inicial

    @property
    def estado_objetivo(self) -> Estado:
        """Retorna o estado objetivo."""
        return Estado(frozenset(), frozenset(self._pessoas), False, 0)

    def add_aresta(self, estado: Estado, custo: int = 0): ...

    def fn_sucessora(self, estado: Estado) -> set[EstadoDestino, ...]:
        """
        Retorna todos os os estados de destino possiveis a partir desse.

        Se o próximo estado for um cliclo, retorna None.
        """
        combinacoes_movimento = estado.get_candidatos()
        resultado = set()
        for pessoas_a_mover in combinacoes_movimento:
            estado_destino = self.fn_transicao(estado, pessoas_a_mover)
            if not estado_destino:  # ciclo
                continue
            resultado.add(estado_destino)
        return resultado

    def fn_transicao(
        self, estado: Estado, pessoas_a_mover: set[Pessoa] | set[Pessoa, Pessoa]
    ) -> EstadoDestino:
        """Retorna o restulado de mover pessoas partindo do estado atual."""
        acao = "ir" if estado.tocha_na_origem else "voltar"
        # validacao
        if acao == "ir":
            for p in pessoas_a_mover:
                if p not in estado.origem:
                    raise RuntimeError("Tentando atravessar uma pessoa que nao esta na origem")
        if acao == "voltar":
            # TODO: podemos considerar nunca queremos voltar com duas pessoas?
            for p in pessoas_a_mover:
                if p not in estado.destino:
                    raise RuntimeError("Tentando voltar com uma pessoa que nao esta no destino")
        else:
            raise ValueError(f"Acao invalida: {acao}")

        # criar proximo estado
        prox_origem = estado.origem.difference(pessoas_a_mover)
        prox_destino = estado.destino.union(pessoas_a_mover)
        prox_tocha_na_origem = not estado.tocha_na_origem
        valor_heuristica = self._fn_heuristica(estado, self.estado_objetivo)
        proximo_estado = Estado(prox_origem, prox_destino, prox_tocha_na_origem, valor_heuristica)
        # evitar ciclos: nao pode voltar para estado ja existente
        if proximo_estado in self._mapa_adjacencia.keys():
            return None
        # criar estado destino com propriedades da transicao acopladas
        custo = max(pessoas_a_mover, key=lambda p: p.custo)
        destino = EstadoDestino(proximo_estado, acao, custo)
        return destino

    def plot(self): ...


def h_padrao(estado: Estado, estado_objetivo: Estado):
    """Funcao heuristica padrao."""
    return 0


# Testes


class TestEstado:
    def test_init(self):
        e0 = Estado.init(custos_iniciais=[])
        assert len(e0.origem) == 0
        assert len(e0.destino) == 0
        assert e0.tocha_na_origem is True

        e1 = Estado.init(custos_iniciais=[1])
        assert len(e1.origem) == 1
        assert len(e1.destino) == 0
        assert e1.tocha_na_origem is True

        e2 = Estado.init(custos_iniciais=[1, 2, 2])
        assert len(e2.origem) == 3
        assert len(e2.destino) == 0
        assert e2.tocha_na_origem is True

        custos = sorted([p.custo for p in e2.origem])
        assert custos == [1, 2, 2]

    def test_candidatos(self):
        p1 = Pessoa(1)
        p2 = Pessoa(1)
        p3 = Pessoa(1)
        origem = frozenset([p1, p2, p3])
        estado = Estado(origem, frozenset(), True)
        candidatos = estado.get_candidatos()
        esperado = {(p1,), (p2,), (p3,), (p1, p2), (p1, p3), (p2, p3)}
        esperado = {frozenset(p) for p in esperado}
        pprint(candidatos)
        assert candidatos == esperado

    def test_transicoes(self): ...


class TestEspacoEstado:
    def test_inicia(self):
        p1 = Pessoa(1)
        p2 = Pessoa(1)
        pessoas = set([p1, p2])
        ee = EspacoEstado(pessoas)
        assert len(ee) == 1
        assert ee.estado_inicial == Estado(frozenset(p1, p2), frozenset(), True, 0)
