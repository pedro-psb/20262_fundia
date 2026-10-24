"""Runner de experimentos: algoritmo × instância × execução → CSVs."""

import csv
import random
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from tp2.algoritmos import ALGORITMOS
from tp2.problema import (
    OPERADORES,
    Manutencao,
    Orcamento,
    OrcamentoEsgotado,
    Registro,
    guloso,
    h,
    ler_instancia,
)

# Orçamento de avaliações e número de execuções independentes por instância.
ORCAMENTOS = {"pequena": 50_000, "media": 150_000, "grande": 300_000}
EXECUCOES = {"pequena": 30, "media": 30, "grande": 10}

CHAVES = ["algoritmo", "operador", "incremental", "instancia", "execucao"]


@dataclass(frozen=True)
class Configuracao:
    """O que rodar em uma execução independente.

    Attributes:
        algoritmo: nome do algoritmo em `ALGORITMOS` (ex.: 'tempera', 'gd-best').
        instancia: nome curto ('pequena', 'media', 'grande') ou caminho do arquivo.
        execucao: índice da execução; também é a semente do gerador aleatório.
        operador: vizinhança usada por `sucessores` e `sucessor_aleatorio`.
        incremental: se `h` reaproveita o prefixo do pai ao avaliar sucessores.
        orcamento: limite de avaliações de h; None usa o padrão da instância.
    """

    algoritmo: str
    instancia: str
    execucao: int
    operador: str = "swap"
    incremental: bool = True
    orcamento: int | None = None


@dataclass
class Resultado:
    """O que uma execução produziu.

    Attributes:
        config: configuração que gerou este resultado.
        instancia: nome da instância lida (sem o prefixo 'manutencao_').
        orcamento: limite de avaliações efetivamente usado.
        melhor_h: menor h avaliado durante a execução.
        melhor_s: solução que atingiu `melhor_h`.
        avaliacoes: avaliações de h gastas (igual a `orcamento` se ele se esgotou).
        tempo: tempo de parede da execução, em segundos.
        historico: pares (avaliações gastas, melhor h) a cada melhora.
        escalares: valores próprios do algoritmo (ex.: passos, restarts, t0, geracoes).
        series: séries próprias do algoritmo, por nome, como pares (x, valor)
            (ex.: 'aceitacao', 'diversidade', 'media_populacao').
    """

    config: Configuracao
    instancia: str
    orcamento: int
    melhor_h: float
    melhor_s: list[int]
    avaliacoes: int
    tempo: float
    historico: list[tuple[int, int]]
    escalares: dict[str, float]
    series: dict[str, list[tuple[float, float]]]

    def chaves(self) -> dict[str, object]:
        c = self.config
        return {
            "algoritmo": c.algoritmo,
            "operador": c.operador,
            "incremental": int(c.incremental),
            "instancia": self.instancia,
            "execucao": c.execucao,
        }

    def prefixo(self) -> str:
        c = self.config
        modo = "" if c.incremental else "-completa"
        return f"{c.algoritmo}_{c.operador}{modo}_{self.instancia}"


def executar(config: Configuracao) -> Resultado:
    """Uma execução independente; a semente é o índice da execução."""
    inst = ler_instancia(config.instancia)
    orcamento = Orcamento(config.orcamento or ORCAMENTOS.get(inst.nome, 50_000))
    reg = Registro(orcamento)
    rng = random.Random(config.execucao)
    prob = Manutencao(inst, orcamento, rng, config.operador, incremental=config.incremental)
    inicio = time.perf_counter()
    try:
        ALGORITMOS[config.algoritmo](prob, rng, reg)
    except OrcamentoEsgotado:
        pass
    tempo = time.perf_counter() - inicio
    return Resultado(
        config,
        inst.nome,
        orcamento.limite,
        orcamento.melhor_h,
        orcamento.melhor_s,
        orcamento.usadas,
        tempo,
        orcamento.historico,
        reg.escalares,
        reg.series,
    )


def _escrever(caminho: Path, campos: list[str], linhas: list[dict[str, object]]) -> Path:
    with caminho.open("w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def salvar(resultados: list[Resultado], saida: Path) -> list[Path]:
    """Grava <prefixo>_execucoes.csv, _historico.csv e _series.csv para cada grupo."""
    saida.mkdir(parents=True, exist_ok=True)
    grupos: dict[str, list[Resultado]] = {}
    for r in resultados:
        grupos.setdefault(r.prefixo(), []).append(r)

    caminhos = []
    for prefixo, grupo in grupos.items():
        escalares = sorted({k for r in grupo for k in r.escalares})
        execucoes = [
            r.chaves()
            | {
                "orcamento": r.orcamento,
                "avaliacoes": r.avaliacoes,
                "melhor_h": r.melhor_h,
                "tempo_s": f"{r.tempo:.4f}",
                "melhor_solucao": " ".join(map(str, r.melhor_s)),
            }
            | {k: r.escalares.get(k, "") for k in escalares}
            for r in grupo
        ]
        campos = [*CHAVES, "orcamento", "avaliacoes", "melhor_h", "tempo_s", "melhor_solucao"]
        caminhos.append(
            _escrever(saida / f"{prefixo}_execucoes.csv", campos + escalares, execucoes)
        )

        historico = [
            r.chaves() | {"avaliacoes": a, "melhor_h": v} for r in grupo for a, v in r.historico
        ]
        caminhos.append(
            _escrever(
                saida / f"{prefixo}_historico.csv", [*CHAVES, "avaliacoes", "melhor_h"], historico
            )
        )

        series = [
            r.chaves() | {"serie": nome, "x": x, "valor": v}
            for r in grupo
            for nome, pontos in r.series.items()
            for x, v in pontos
        ]
        caminhos.append(
            _escrever(saida / f"{prefixo}_series.csv", [*CHAVES, "serie", "x", "valor"], series)
        )
    return caminhos


def carregar(diretorio: Path, tipo: str) -> list[dict[str, str]]:
    """Concatena as linhas de todos os <prefixo>_<tipo>.csv do diretório."""
    linhas: list[dict[str, str]] = []
    for caminho in sorted(diretorio.glob(f"*_{tipo}.csv")):
        with caminho.open(newline="") as f:
            linhas.extend(csv.DictReader(f))
    return linhas


def rodar(
    algoritmo: str,
    instancias: list[str],
    saida: Path,
    operador: str = "swap",
    incremental: bool = True,
    execucoes: int | None = None,
    orcamento: int | None = None,
    processos: int | None = None,
) -> list[Path]:
    configs = [
        Configuracao(algoritmo, inst, e, operador, incremental, orcamento)
        for inst in instancias
        for e in range(execucoes or EXECUCOES.get(inst, 10))
    ]
    with ProcessPoolExecutor(processos) as pool:
        resultados = list(pool.map(executar, configs))
    return salvar(resultados, saida)


def verificar() -> str:
    """h da permutação identidade e da solução gulosa na instância pequena."""
    inst = ler_instancia("pequena")
    identidade = list(range(1, inst.n + 1))
    perm = guloso(inst)
    return "\n".join(
        [
            f"instância pequena (n = {inst.n})",
            f"h(identidade) = {h(inst, identidade)}",
            f"guloso = {perm}",
            f"h(guloso) = {h(inst, perm)}",
        ]
    )


def medir_incremental(instancias: list[str], saida: Path, amostras: int = 5000) -> Path:
    """Tempo médio por avaliação, completa × incremental, em sucessores aleatórios."""
    linhas: list[dict[str, object]] = []
    for nome in instancias:
        inst = ler_instancia(nome)
        for operador in OPERADORES:
            tempos = {}
            for incremental in (False, True):
                prob = Manutencao(
                    inst,
                    Orcamento(amostras + 1),
                    random.Random(0),
                    operador,
                    incremental=incremental,
                )
                s = prob.solucao_aleatoria()
                prob.h(s)
                vizinhos = [prob.sucessor_aleatorio(s) for _ in range(amostras)]
                inicio = time.perf_counter()
                for s2 in vizinhos:
                    prob.h(s2)
                tempos[incremental] = (time.perf_counter() - inicio) / amostras * 1e6
            linhas.append(
                {
                    "instancia": inst.nome,
                    "operador": operador,
                    "completa_us": f"{tempos[False]:.2f}",
                    "incremental_us": f"{tempos[True]:.2f}",
                    "speedup": f"{tempos[False] / tempos[True]:.2f}",
                }
            )
    saida.mkdir(parents=True, exist_ok=True)
    campos = ["instancia", "operador", "completa_us", "incremental_us", "speedup"]
    return _escrever(saida / "incremental.csv", campos, linhas)
