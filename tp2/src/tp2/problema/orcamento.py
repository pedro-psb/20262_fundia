"""Contagem de avaliações com orçamento fixo e registro de dados extras da execução."""

import math
from dataclasses import dataclass, field


class OrcamentoEsgotado(Exception):
    pass


@dataclass
class Orcamento:
    """Conta avaliações de h, para exatamente no limite e guarda o histórico de melhoras."""

    limite: int
    usadas: int = 0
    melhor_h: float = math.inf
    melhor_s: list[int] = field(default_factory=list)
    historico: list[tuple[int, int]] = field(default_factory=list)

    def contar(self, valor: int, s: list[int]) -> None:
        if self.usadas >= self.limite:
            raise OrcamentoEsgotado
        self.usadas += 1
        if valor < self.melhor_h:
            self.melhor_h = valor
            self.melhor_s = list(s)
            self.historico.append((self.usadas, valor))

    def restantes(self) -> int:
        return self.limite - self.usadas


@dataclass
class Registro:
    """Dados extras de uma execução; sobrevive à interrupção por orçamento."""

    orcamento: Orcamento
    escalares: dict[str, float] = field(default_factory=dict)
    series: dict[str, list[tuple[float, float]]] = field(default_factory=dict)

    def somar(self, nome: str, valor: float = 1) -> None:
        self.escalares[nome] = self.escalares.get(nome, 0) + valor

    def serie(self, nome: str, valor: float, x: float | None = None) -> None:
        """Acrescenta um ponto; x é, por padrão, o número de avaliações já gastas."""
        self.series.setdefault(nome, []).append((self.orcamento.usadas if x is None else x, valor))
