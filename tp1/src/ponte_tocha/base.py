from collections.abc import Iterable, Sequence
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

    @classmethod
    def factory(cls, custos: Sequence[int]) -> frozenset["Pessoa"]:
        """Cria um conjunto de pessoas a partir de seus custos de travessia."""
        return frozenset(cls(custo) for custo in custos)

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
    def new(
        cls,
        origem: Iterable[Pessoa],
        destino: Iterable[Pessoa],
        tocha_na_origem: bool,
        estimativa_heuristica: int = 0,
    ) -> "Estado":
        """Aceita qualquer sequência de pessoas, mas armazena sempre como frozenset."""
        return cls(frozenset(origem), frozenset(destino), tocha_na_origem, estimativa_heuristica)

    def is_estado_final(self) -> bool:
        origem_vazia = len(self.origem) == 0
        destino_nao_vazio = len(self.destino) != 0
        tocha_no_destino = not self.tocha_na_origem
        return origem_vazia and destino_nao_vazio and tocha_no_destino

    def is_estado_inicial(self) -> bool:
        origem_nao_vazia = len(self.origem) != 0
        destino_vazio = len(self.destino) == 0
        return origem_nao_vazia and destino_vazio and self.tocha_na_origem

    def get_candidatos(self) -> list[frozenset[Pessoa]]:
        """
        Retorna a lista de candidatos a atravessar a ponte, em ordem determinística.

        Um ou duas pessoas podem atravessar a ponte ao mesmo tempo. A ordem
        não depende da iteração de um ``set`` (que varia com o hash dos
        objetos): as pessoas são primeiro ordenadas por (custo, id).

        Exemplo:
            >>> estado = Estado.new({1,2,3}, {})
            >>> estado.get_candidatos()
            [{1}, {2}, {3}, {1,2}, {1,3}, {2,3}]
        """
        lado_com_tocha = self.origem if self.tocha_na_origem else self.destino
        pessoas = sorted(lado_com_tocha, key=lambda p: (p.custo, p.id))

        candidatos = [frozenset((p,)) for p in pessoas]
        for i, p_i in enumerate(pessoas):
            for p_j in pessoas[i + 1 :]:
                candidatos.append(frozenset((p_i, p_j)))
        return candidatos

    def __repr__(self) -> str:
        """Representacao compacta para debugging."""
        compacto = (
            set(self.origem),
            set(self.destino),
            self.tocha_na_origem,
            self.estimativa_heuristica,
        )
        return str(compacto)


class Movimento(StrEnum):
    IR = "ir"
    VOLTAR = "voltar"


@dataclass(frozen=True)
class Sucessor:
    """Representa um proximo estado de destino e com sua acao e peso."""

    estado: Estado
    acao: Movimento
    custo: int = 0

    def __repr__(self) -> str:
        classname = self.__class__.__name__
        return f"{classname}({self.estado}, {str(self.acao)}, {self.custo})"


class EspacoEstado:
    def __init__(self, pessoas: Sequence[Pessoa], fn_heuristica=None):
        self._fn_heuristica = fn_heuristica or h_padrao
        self._pessoas = pessoas
        estado_inicial = Estado.new(pessoas, set(), True, 0)
        valor_heuristica = self._fn_heuristica(estado_inicial, self.estado_objetivo)
        self._estado_inicial = estado_inicial._replace(estimativa_heuristica=valor_heuristica)

    @property
    def estado_inicial(self) -> Estado:
        """Retorna o estado inicial."""
        return self._estado_inicial

    @property
    def estado_objetivo(self) -> Estado:
        """Retorna o estado objetivo."""
        return Estado.new(set(), self._pessoas, False, 0)

    def fn_sucessora(self, estado: Estado) -> list[Sucessor]:
        """Retorna todos os estados de destino possiveis a partir desse, em ordem determinística.

        Não evita ciclos: cabe ao algoritmo de busca controlar quais estados
        já foram visitados.
        """
        if estado.is_estado_final():
            return []
        combinacoes_movimento = estado.get_candidatos()
        return [
            self.acao_mover(estado, pessoas_a_mover) for pessoas_a_mover in combinacoes_movimento
        ]

    def acao_mover(self, estado: Estado, pessoas_a_mover: Iterable[Pessoa]) -> Sucessor:
        """Retorna o restulado de mover pessoas partindo do estado atual."""
        acao = Movimento.IR if estado.tocha_na_origem else Movimento.VOLTAR
        # validacao
        if acao == Movimento.IR:
            for p in pessoas_a_mover:
                if p not in estado.origem:
                    raise RuntimeError("Tentando atravessar uma pessoa que nao esta na origem")
        elif acao == Movimento.VOLTAR:
            # TODO: podemos considerar que nunca queremos voltar com duas pessoas?
            for p in pessoas_a_mover:
                if p not in estado.destino:
                    raise RuntimeError("Tentando voltar com uma pessoa que nao esta no destino")
        else:
            raise ValueError(f"Acao invalida: {acao}")

        # criar proximo estado
        if acao == Movimento.IR:
            prox_origem = estado.origem.difference(pessoas_a_mover)
            prox_destino = estado.destino.union(pessoas_a_mover)
        else:
            prox_origem = estado.origem.union(pessoas_a_mover)
            prox_destino = estado.destino.difference(pessoas_a_mover)
        prox_tocha_na_origem = not estado.tocha_na_origem
        proximo_estado = Estado.new(prox_origem, prox_destino, prox_tocha_na_origem)
        valor_heuristica = self._fn_heuristica(proximo_estado, self.estado_objetivo)
        proximo_estado = proximo_estado._replace(estimativa_heuristica=valor_heuristica)
        # criar estado destino com propriedades da transicao acopladas
        custo = max(p.custo for p in pessoas_a_mover)
        return Sucessor(proximo_estado, acao, custo)


def h_padrao(estado: Estado, estado_objetivo: Estado):
    """Funcao heuristica padrao."""
    return 0


def h_max_origem(estado: Estado, estado_objetivo: Estado) -> int:
    """Estima o custo restante pelo maior tempo de quem ainda esta na origem.

    Para custos nao negativos, e admissivel: a pessoa mais lenta na origem
    ainda precisa atravessar, custando pelo menos o seu tempo. No objetivo,
    a origem esta vazia e a estimativa e zero.

    Tambem e consistente: numa ida, o custo cobre qualquer reducao de h;
    numa volta, adicionar pessoas a origem nao reduz h. Assim,
    h(estado) <= custo_movimento + h(proximo_estado) em toda transicao.
    """
    return max((p.custo for p in estado.origem), default=0)


# Testes


class TestEstado:
    def test_init(self):
        e0 = Estado.new(Pessoa.factory([]), set(), True)
        assert len(e0.origem) == 0
        assert len(e0.destino) == 0
        assert e0.tocha_na_origem is True

        e1 = Estado.new(Pessoa.factory([1]), set(), True)
        assert len(e1.origem) == 1
        assert len(e1.destino) == 0
        assert e1.tocha_na_origem is True

        e2 = Estado.new(Pessoa.factory([1, 2, 2]), set(), True)
        assert len(e2.origem) == 3
        assert len(e2.destino) == 0
        assert e2.tocha_na_origem is True

        custos = sorted([p.custo for p in e2.origem])
        assert custos == [1, 2, 2]

    def test_candidatos(self):
        p1 = Pessoa(1)
        p2 = Pessoa(1)
        p3 = Pessoa(1)
        origem = {p1, p2, p3}
        estado = Estado.new(origem, set(), True)
        candidatos = estado.get_candidatos()
        esperado = {(p1,), (p2,), (p3,), (p1, p2), (p1, p3), (p2, p3)}
        esperado = {frozenset(p) for p in esperado}
        assert len(candidatos) == len(esperado)  # sem duplicatas
        assert set(candidatos) == esperado

    def test_transicoes(self): ...


class TestEspacoEstado:
    def test_inicia(self):
        pessoas = {Pessoa(1), Pessoa(1)}
        ee = EspacoEstado(pessoas)
        assert ee.estado_inicial == Estado.new(pessoas, set(), True, 0)

    def test_heuristica_inicial(self):
        ee = EspacoEstado(Pessoa.factory([1, 2, 5]), fn_heuristica=h_max_origem)
        assert ee.estado_inicial.estimativa_heuristica == 5

    def test_heuristica_objetivo(self):
        pessoas = Pessoa.factory([1, 2])
        ee = EspacoEstado(pessoas, fn_heuristica=h_max_origem)
        assert h_max_origem(ee.estado_objetivo, ee.estado_objetivo) == 0

        sucessor = ee.acao_mover(ee.estado_inicial, pessoas)
        assert sucessor.estado == ee.estado_objetivo
        assert sucessor.estado.estimativa_heuristica == 0

    def test_heuristica_sucessor_e_retorno(self):
        p1, p2, p5 = Pessoa(1), Pessoa(2), Pessoa(5)
        ee = EspacoEstado([p1, p2, p5], fn_heuristica=h_max_origem)

        ida = ee.acao_mover(ee.estado_inicial, {p5})
        assert ida.estado.origem == frozenset({p1, p2})
        assert ida.estado.estimativa_heuristica == 2

        volta = ee.acao_mover(ida.estado, {p5})
        assert volta.estado == ee.estado_inicial
        assert volta.estado.estimativa_heuristica == 5

    def test_heuristica_consistente_nos_estados_alcancaveis(self):
        for custos in ([1, 2, 5], [1, 2, 5, 10]):
            ee = EspacoEstado(Pessoa.factory(custos), fn_heuristica=h_max_origem)
            pendentes = [ee.estado_inicial]
            visitados = set()

            while pendentes:
                estado = pendentes.pop()
                chave = (estado.origem, estado.destino, estado.tocha_na_origem)
                if chave in visitados:
                    continue
                visitados.add(chave)

                h_atual = h_max_origem(estado, ee.estado_objetivo)
                assert estado.estimativa_heuristica == h_atual
                for sucessor in ee.fn_sucessora(estado):
                    h_sucessor = h_max_origem(sucessor.estado, ee.estado_objetivo)
                    assert sucessor.estado.estimativa_heuristica == h_sucessor
                    assert h_atual <= sucessor.custo + h_sucessor
                    pendentes.append(sucessor.estado)

    def test_funcao_sucessora(self):
        p1 = Pessoa(1)
        p2 = Pessoa(1)
        pessoas = {p1, p2}
        ee = EspacoEstado(pessoas)
        s0 = ee.estado_inicial
        assert s0 == Estado.new({p1, p2}, {}, True, 0)

        # expandir estado s0
        result = ee.fn_sucessora(s0)
        s1 = Estado.new({p2}, {p1}, False, 0)
        s2 = Estado.new({p1}, {p2}, False, 0)
        s3 = Estado.new(set(), {p1, p2}, False, 0)
        esperado = {
            Sucessor(s1, Movimento.IR, custo=1),
            Sucessor(s2, Movimento.IR, custo=1),
            Sucessor(s3, Movimento.IR, custo=1),
        }
        print()
        pprint(esperado)
        assert len(result) == len(esperado)  # sem duplicatas
        assert set(result) == esperado

        # expandir estado s1
        # - a tocha esta no lado B, entao o unico movimento é p1 voltar
        # - isso leva de volta ao estado inicial s0; fn_sucessora não evita esse
        #   ciclo, isso fica a cargo do algoritmo de busca (via seu visitados)
        result = ee.fn_sucessora(s1)
        assert set(result) == {Sucessor(s0, Movimento.VOLTAR, custo=1)}

        # expandir estado s2 (simetrico a s1)
        result = ee.fn_sucessora(s2)
        assert set(result) == {Sucessor(s0, Movimento.VOLTAR, custo=1)}

        # expandir estado s3
        # o estado é a funcao objetivo, nada mais a expandir
        result = ee.fn_sucessora(s3)
        assert result == []
