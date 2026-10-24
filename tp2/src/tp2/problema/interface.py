"""Interface comum entre algoritmos e problema, e sua implementação para a manutenção."""

import random
from collections.abc import Iterator
from typing import Protocol

from .avaliacao import cronograma, estender, h, h_sufixo
from .instancia import Instancia
from .operadores import OPERADORES, Operador, cruzamento_ox
from .orcamento import Orcamento


class Solucao(list[int]):
    """Permutação que sabe de onde veio e guarda o memo da recursão de C.

    Um sucessor guarda o pai e a primeira posição alterada `k`, para que sua avaliação
    percorra só o sufixo. O memo só é montado quando a solução vira pai de outras.
    """

    __slots__ = ("conclusao", "custo", "pai", "k")

    def __init__(self, perm: list[int], pai: "Solucao | None" = None, k: int = 0) -> None:
        super().__init__(perm)
        self.conclusao: list[int] | None = None
        self.custo: list[int] | None = None
        self.pai = pai
        self.k = k


class Problema(Protocol):
    """Interface comum entre os algoritmos e o problema.

    Os algoritmos só conhecem estes métodos. Soluções são permutações dos ativos 1..n
    (a ordem de visita) e `h` é sempre de minimização.
    """

    def solucao_aleatoria(self) -> list[int]:
        """Sorteia uma permutação uniforme, usada como ponto de partida."""
        ...

    def h(self, s: list[int]) -> int:
        """Avalia s; cada chamada conta uma avaliação no orçamento, mesmo que repetida.

        Args:
            s: solução a avaliar.

        Raises:
            OrcamentoEsgotado: se o orçamento de avaliações já foi todo gasto.
        """
        ...

    def sucessores(self, s: list[int]) -> Iterator[list[int]]:
        """Itera sobre todos os sucessores de s na vizinhança configurada, sem avaliá-los.

        Args:
            s: solução corrente, cuja vizinhança é percorrida.
        """
        ...

    def sucessor_aleatorio(self, s: list[int]) -> list[int]:
        """Sorteia um único sucessor de s na vizinhança configurada, sem avaliá-lo.

        Args:
            s: solução corrente.
        """
        ...

    def cruzamento(self, a: list[int], b: list[int]) -> list[int]:
        """Recombina dois pais em um filho que continua sendo uma permutação válida.

        Args:
            a: primeiro pai, do qual o filho herda um trecho contíguo.
            b: segundo pai, que dá a ordem dos ativos restantes.
        """
        ...

    def mutacao(self, s: list[int]) -> list[int]:
        """Aplica uma pequena perturbação aleatória e devolve uma nova solução.

        Args:
            s: solução a perturbar; não é modificada.
        """
        ...

    def tamanho_vizinhanca(self) -> int:
        """Número de sucessores que `sucessores` gera para qualquer solução."""
        ...

    def restantes(self) -> int:
        """Número de avaliações de `h` que ainda cabem no orçamento."""
        ...


class Manutencao:
    """Implementação de `Problema` para o sequenciamento de manutenção.

    Toda chamada a `h` conta uma avaliação no orçamento, inclusive reavaliações.

    Args:
        inst: instância a resolver.
        orcamento: contador de avaliações da execução.
        rng: gerador de números aleatórios da execução; o mesmo objeto deve ser passado
            ao algoritmo, para que a execução dependa de uma única semente.
        operador: vizinhança usada por `sucessores` e `sucessor_aleatorio`.
        mutacao: operador usado por `mutacao`.
        incremental: se `h` reaproveita o prefixo do pai ao avaliar sucessores.
    """

    def __init__(
        self,
        inst: Instancia,
        orcamento: Orcamento,
        rng: random.Random,
        operador: str = "swap",
        mutacao: str = "swap",
        incremental: bool = True,
    ) -> None:
        self.inst = inst
        self.orcamento = orcamento
        self.rng = rng
        self.operador = OPERADORES[operador]
        self.operador_mutacao = OPERADORES[mutacao]
        self.incremental = incremental

    def solucao_aleatoria(self) -> Solucao:
        perm = list(range(1, self.inst.n + 1))
        self.rng.shuffle(perm)
        return Solucao(perm)

    def h(self, s: list[int]) -> int:
        valor = self._avaliar_incremental(s) if self.incremental else h(self.inst, s)
        self.orcamento.contar(valor, s)
        return valor

    def _avaliar_incremental(self, s: list[int]) -> int:
        if isinstance(s, Solucao) and s.pai is not None:
            conclusao, custo = self._memo(s.pai)
            return h_sufixo(self.inst, s, s.k, conclusao, custo)
        return h(self.inst, s)

    def _memo(self, s: "Solucao") -> tuple[list[int], list[int]]:
        if s.conclusao is None or s.custo is None:
            pai = s.pai
            if pai is not None and pai.conclusao is not None and pai.custo is not None:
                s.conclusao, s.custo = estender(self.inst, s, s.k, pai.conclusao, pai.custo)
            else:
                s.conclusao, s.custo = cronograma(self.inst, s)
            s.pai = None
        return s.conclusao, s.custo

    def _vizinho(self, s: list[int], i: int, j: int, op: Operador) -> Solucao:
        pai = s if self.incremental and isinstance(s, Solucao) else None
        return Solucao(op.aplicar(s, i, j), pai, min(i, j))

    def sucessores(self, s: list[int]) -> Iterator[Solucao]:
        for i, j in self.operador.movimentos(self.inst.n):
            yield self._vizinho(s, i, j, self.operador)

    def sucessor_aleatorio(self, s: list[int]) -> Solucao:
        return self._vizinho(s, *self.operador.sortear(self.inst.n, self.rng), self.operador)

    def cruzamento(self, a: list[int], b: list[int]) -> Solucao:
        i, j = sorted(self.rng.sample(range(self.inst.n), 2))
        return Solucao(cruzamento_ox(a, b, i, j))

    def mutacao(self, s: list[int]) -> Solucao:
        op = self.operador_mutacao
        return self._vizinho(s, *op.sortear(self.inst.n, self.rng), op)

    def tamanho_vizinhanca(self) -> int:
        return self.operador.tamanho(self.inst.n)

    def restantes(self) -> int:
        return self.orcamento.restantes()
