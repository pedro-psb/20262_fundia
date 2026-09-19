from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import NamedTuple
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Pessoa:
    """
    A representação de uma pessoa.

    Args:
        id: Identificador único de uma pessoa.
        custo: O custo (em minutos) de travessia dessa pessoa
    """

    custo: int
    id: UUID = field(default_factory=uuid4)


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
            combinacoes.add(frozenset(p_i))
            for p_j in self.origem:
                combinacoes.add(frozenset(p_i, p_j))
        return combinacoes

    def repr_compacta(self):
        compacto = (self.origem, self.destino, self.tocha_na_origem)
        print(compacto)


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


def test_espaco_estado_inicia():
    estado_0 = Estado({1}, {}, 0)
    print(estado_0.repr_compacta())
    ee = EspacoEstado()
    ee.gerar()
    ee.as_dict()
