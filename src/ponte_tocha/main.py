from collections.abc import Sequence
from dataclasses import dataclass, field
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
        origem:
            O conjunto de origem. Representa as pessoas do lado inicial da
            ponte. Uma pessoa é representada como o tempo em minutos que ela
            demora para atravessar.
        destino:
            O conjunto de destino. Representa as pessoas que chegaram estão outro lado.
        tocha_na_origem:
            Verdadeira se a tocha está atualmente no lado inicial da ponte.
    """

    origem: frozenset[Pessoa]
    destino: frozenset[Pessoa]
    tocha_na_origem: bool

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
        compacto = (self.origem, self.destino, self.tocha_na_origem)
        return str(compacto)


def f_sucessora(estado: Estado): ...


class EspacoEstado:
    def __init__(self): ...

    def gerar(self): ...

    def as_dict(self): ...


ESTADO_INICIAL = Estado(frozenset(), frozenset(), True)

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


def test_espaco_estado_inicia():
    ee = EspacoEstado()
    ee.gerar()
    ee.as_dict()
