"""Tabelas e figuras finais do relatório a partir dos CSVs brutos do runner.

Gera, no diretório de saída:
- resumo.csv e pvalores.csv, com todas as configurações encontradas;
- tab-<rótulo>.tex, as linhas de cada tabela do relatório (entre \\midrule e \\bottomrule);
- boxplots.png, convergencia.png, sa_aceitacao.png e ag_diversidade.png.

Sem dados para uma célula, a tabela mostra "--"; assim o relatório compila antes da rodada.
"""

import csv
import itertools
import math
import statistics
from bisect import bisect_right
from collections.abc import Iterable
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from scipy.stats import mannwhitneyu  # noqa: E402

from tp2.experimento import CHAVES, carregar  # noqa: E402
from tp2.problema import NOMES_INSTANCIAS, REFERENCIAS  # noqa: E402

plt.style.use(["seaborn-v0_8-whitegrid", "seaborn-v0_8-muted"])

Linha = dict[str, str]
PADRAO = {*CHAVES, "orcamento", "avaliacoes", "melhor_h", "tempo_s", "melhor_solucao"}

# Configurações que aparecem no relatório. GD+RR é a descida com best improvement; a
# comparação das vizinhanças usa first improvement, que dá mais passos no mesmo orçamento.
PRINCIPAIS = {"GD+RR": "gd-best", "SA": "tempera", "AG": "genetico"}
VARIANTES_GD = {"best": "gd-best", "first": "gd-first", "aleatória": "gd-aleatorio"}
GD_VIZINHANCAS = "gd-first"
AG_SEM_CRUZAMENTO = "genetico-sem-cruzamento"
EXIBICAO_INSTANCIAS = {"pequena": "pequena", "media": "intermediária", "grande": "grande"}
EXIBICAO_OPERADORES = {"swap": "Swap", "insertion": "Insertion", "2-opt": "2-opt"}
VAZIO = "--"


def _rotulo(linha: Linha) -> str:
    rotulo = linha["algoritmo"]
    if linha["operador"] != "swap":
        rotulo += f" ({linha['operador']})"
    if linha["incremental"] != "1":
        rotulo += ", completa"
    return rotulo


def _instancias(linhas: Iterable[Linha]) -> list[str]:
    nomes = {linha["instancia"] for linha in linhas}
    ordem = {nome: i for i, nome in enumerate(NOMES_INSTANCIAS)}
    return sorted(nomes, key=lambda nome: (ordem.get(nome, len(ordem)), nome))


def _agrupar(linhas: Iterable[Linha], chave) -> dict:
    grupos: dict = {}
    for linha in linhas:
        grupos.setdefault(chave(linha), []).append(linha)
    return grupos


def _numero(valor: str | None) -> float | None:
    try:
        return float(valor) if valor is not None else None
    except ValueError:
        return None


def _escrever_csv(caminho: Path, linhas: list[dict[str, object]]) -> Path:
    campos = list(dict.fromkeys(k for linha in linhas for k in linha))
    with caminho.open("w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
    return caminho


def _mann_whitney(a: list[float], b: list[float]) -> float:
    if len(set(a) | set(b)) == 1:
        return 1.0
    return float(mannwhitneyu(a, b).pvalue)


# Resumos em CSV


def resumo(execucoes: list[Linha]) -> list[dict[str, object]]:
    """Média, desvio, mediana, mínimo, gap e médias dos extras por instância × configuração."""
    linhas: list[dict[str, object]] = []
    grupos = _agrupar(execucoes, lambda r: (r["instancia"], _rotulo(r)))
    for instancia in _instancias(execucoes):
        for (inst, rotulo), grupo in sorted(grupos.items()):
            if inst != instancia:
                continue
            hs = [float(r["melhor_h"]) for r in grupo]
            linha: dict[str, object] = {
                "instancia": instancia,
                "configuracao": rotulo,
                "execucoes": len(hs),
                "media": round(statistics.mean(hs), 2),
                "desvio": round(statistics.stdev(hs), 2) if len(hs) > 1 else 0.0,
                "mediana": statistics.median(hs),
                "minimo": min(hs),
                "maximo": max(hs),
            }
            if (ref := REFERENCIAS.get(instancia)) is not None:
                linha["referencia"] = ref
                linha["gap_medio"] = round((statistics.mean(hs) - ref) / ref, 4)
                linha["gap_minimo"] = round((min(hs) - ref) / ref, 4)
                linha["atingiu_referencia"] = sum(v <= ref for v in hs)
            linha["tempo_medio_s"] = round(statistics.mean(float(r["tempo_s"]) for r in grupo), 3)
            linha["avaliacoes_media"] = statistics.mean(int(r["avaliacoes"]) for r in grupo)
            for extra in sorted({k for r in grupo for k in r} - PADRAO):
                valores = [v for r in grupo if (v := _numero(r.get(extra))) is not None]
                if valores:
                    linha[extra] = round(statistics.mean(valores), 6)
            linhas.append(linha)
    return linhas


def pvalores(execucoes: list[Linha]) -> list[dict[str, object]]:
    """Mann–Whitney bilateral entre cada par de configurações, por instância."""
    linhas: list[dict[str, object]] = []
    for instancia in _instancias(execucoes):
        grupos = _agrupar([r for r in execucoes if r["instancia"] == instancia], _rotulo)
        for a, b in itertools.combinations(sorted(grupos), 2):
            ha = [float(r["melhor_h"]) for r in grupos[a]]
            hb = [float(r["melhor_h"]) for r in grupos[b]]
            linhas.append(
                {
                    "instancia": instancia,
                    "a": a,
                    "b": b,
                    "mediana_a": statistics.median(ha),
                    "mediana_b": statistics.median(hb),
                    "p_valor": f"{_mann_whitney(ha, hb):.3g}",
                }
            )
    return linhas


# Tabelas do relatório


class Dados:
    """Acesso às execuções por algoritmo × instância (vizinhança swap e avaliação incremental,
    salvo indicação)."""

    def __init__(self, execucoes: list[Linha], incremental: list[Linha]) -> None:
        self.grupos = _agrupar(
            execucoes,
            lambda r: (r["algoritmo"], r["instancia"], r["operador"], r["incremental"]),
        )
        self.incremental = incremental

    def execucoes(self, algoritmo: str, instancia: str, operador: str = "swap") -> list[Linha]:
        return self.grupos.get((algoritmo, instancia, operador, "1"), [])

    def hs(self, algoritmo: str, instancia: str, operador: str = "swap") -> list[float]:
        return [float(r["melhor_h"]) for r in self.execucoes(algoritmo, instancia, operador)]

    def media(self, algoritmo: str, instancia: str, chave: str) -> float | None:
        valores = [
            v
            for r in self.execucoes(algoritmo, instancia)
            if (v := _numero(r.get(chave))) is not None
        ]
        return statistics.mean(valores) if valores else None


def _p(valor: float) -> str:
    return "$<$0.001" if valor < 0.001 else f"{valor:.3f}"


def _num(valor: float | None, casas: int = 0) -> str:
    return VAZIO if valor is None else f"{valor:.{casas}f}"


def _media_dp(hs: list[float]) -> str:
    if not hs:
        return VAZIO
    desvio = statistics.stdev(hs) if len(hs) > 1 else 0.0
    return f"{statistics.mean(hs):.1f} $\\pm$ {desvio:.1f}"


def _escrever_tabela(caminho: Path, grupos: list[list[list[str]]]) -> Path:
    """Grava as linhas de uma tabela; grupos consecutivos são separados por \\midrule."""
    blocos = ["\n".join(" & ".join(celulas) + r" \\" for celulas in grupo) for grupo in grupos]
    caminho.write_text("\n\\midrule\n".join(blocos) + "\n")
    return caminho


def _primeira(instancia: str, i: int) -> str:
    return EXIBICAO_INSTANCIAS[instancia] if i == 0 else ""


def tabela_principal(d: Dados) -> list[list[list[str]]]:
    grupos = []
    for instancia in NOMES_INSTANCIAS:
        grupo = []
        for i, (nome, algoritmo) in enumerate(PRINCIPAIS.items()):
            hs = d.hs(algoritmo, instancia)
            linha = [
                _primeira(instancia, i),
                nome,
                _media_dp(hs),
                _num(statistics.median(hs) if hs else None),
                _num(min(hs) if hs else None),
            ]
            if instancia == "pequena":
                ref = REFERENCIAS[instancia]
                gaps = [100 * (v - ref) / ref for v in hs]
                linha += [
                    _num(statistics.mean(gaps) if gaps else None, 1) + ("\\%" if gaps else ""),
                    _num(min(gaps) if gaps else None, 1) + ("\\%" if gaps else ""),
                ]
            else:
                linha.append(r"\multicolumn{2}{c}{--}")
            grupo.append(linha)
        grupos.append(grupo)
    return grupos


def tabela_pvalores(d: Dados) -> list[list[list[str]]]:
    linhas = []
    for instancia in NOMES_INSTANCIAS:
        linha = [EXIBICAO_INSTANCIAS[instancia]]
        for a, b in itertools.combinations(PRINCIPAIS, 2):
            ha, hb = d.hs(PRINCIPAIS[a], instancia), d.hs(PRINCIPAIS[b], instancia)
            if not ha or not hb:
                linha.append(VAZIO)
                continue
            melhor = a if statistics.median(ha) <= statistics.median(hb) else b
            linha.append(f"{_p(_mann_whitney(ha, hb))} ({melhor})")
        linhas.append(linha)
    return [linhas]


def tabela_tempo(d: Dados) -> list[list[list[str]]]:
    grupos = []
    for instancia in NOMES_INSTANCIAS:
        grupo = []
        for i, (nome, algoritmo) in enumerate(PRINCIPAIS.items()):
            avaliacoes = d.media(algoritmo, instancia, "avaliacoes")
            tempo = d.media(algoritmo, instancia, "tempo_s")
            por_segundo = avaliacoes / tempo if avaliacoes and tempo else None
            grupo.append(
                [_primeira(instancia, i), nome, _num(avaliacoes), _num(tempo, 2), _num(por_segundo)]
            )
        grupos.append(grupo)
    return grupos


def tabela_incremental(d: Dados) -> list[list[list[str]]]:
    if not d.incremental:
        return [[[VAZIO] * 5]]
    grupos = _agrupar(d.incremental, lambda r: r["instancia"])
    return [
        [
            [
                _primeira(instancia, i),
                EXIBICAO_OPERADORES.get(r["operador"], r["operador"]),
                r["completa_us"],
                r["incremental_us"],
                r["speedup"],
            ]
            for i, r in enumerate(grupos[instancia])
        ]
        for instancia in NOMES_INSTANCIAS
        if instancia in grupos
    ]


def tabela_vizinhancas(d: Dados) -> list[list[list[str]]]:
    linhas = []
    for operador, nome in EXIBICAO_OPERADORES.items():
        linha = [nome]
        for instancia in NOMES_INSTANCIAS:
            hs = d.hs(GD_VIZINHANCAS, instancia, operador)
            linha.append(f"{_media_dp(hs)} / {min(hs):.0f}" if hs else VAZIO)
        linhas.append(linha)
    return [linhas]


def tabela_gd_passos(d: Dados) -> list[list[list[str]]]:
    grupos = []
    for instancia in NOMES_INSTANCIAS:
        grupo = []
        for i, (nome, algoritmo) in enumerate(VARIANTES_GD.items()):
            hs = d.hs(algoritmo, instancia)
            grupo.append(
                [
                    _primeira(instancia, i),
                    nome,
                    _num(d.media(algoritmo, instancia, "passos"), 1),
                    _num(d.media(algoritmo, instancia, "restarts"), 1),
                    _num(statistics.mean(hs) if hs else None, 1),
                ]
            )
        grupos.append(grupo)
    return grupos


def tabela_otimos_locais(d: Dados) -> list[list[list[str]]]:
    ref = REFERENCIAS["pequena"]
    linhas = []
    for nome, algoritmo in PRINCIPAIS.items():
        hs = d.hs(algoritmo, "pequena")
        otimos = (
            _num(d.media(algoritmo, "pequena", "otimos_distintos"), 1)
            if algoritmo.startswith("gd-")
            else "n/a"
        )
        linhas.append([nome, otimos, str(sum(v <= ref for v in hs)) if hs else VAZIO])
    return [linhas]


def tabela_sa_parametros(d: Dados) -> list[list[list[str]]]:
    linhas = []
    for instancia in NOMES_INSTANCIAS:
        tem = bool(d.execucoes("tempera", instancia))
        linhas.append(
            [
                EXIBICAO_INSTANCIAS[instancia],
                _num(d.media("tempera", instancia, "delta_medio"), 1),
                _num(d.media("tempera", instancia, "t0"), 1),
                _num(d.media("tempera", instancia, "tf"), 2),
                _num(d.media("tempera", instancia, "alfa"), 6),
                "1" if tem else VAZIO,
            ]
        )
    return [linhas]


def tabela_ag_parametros(d: Dados) -> list[list[list[str]]]:
    linhas = []
    for instancia in NOMES_INSTANCIAS:
        linha = [EXIBICAO_INSTANCIAS[instancia]]
        for chave, casas in (("tamanho", 0), ("pc", 2), ("pm", 2), ("torneio", 0), ("elite", 0)):
            linha.append(_num(d.media("genetico", instancia, chave), casas))
        linhas.append(linha)
    return [linhas]


def tabela_experimento_ag(d: Dados) -> list[list[list[str]]]:
    grupos = []
    for instancia in NOMES_INSTANCIAS:
        com, sem = d.hs("genetico", instancia), d.hs(AG_SEM_CRUZAMENTO, instancia)
        p = _p(_mann_whitney(com, sem)) if com and sem else VAZIO
        grupos.append(
            [
                [EXIBICAO_INSTANCIAS[instancia], "com cruzamento", _media_dp(com), p],
                ["", "sem cruzamento", _media_dp(sem), ""],
            ]
        )
    return grupos


TABELAS = {
    "tab-principal": tabela_principal,
    "tab-pvalores": tabela_pvalores,
    "tab-tempo": tabela_tempo,
    "tab-incremental": tabela_incremental,
    "tab-vizinhancas": tabela_vizinhancas,
    "tab-gd-passos": tabela_gd_passos,
    "tab-otimos-locais": tabela_otimos_locais,
    "tab-sa-parametros": tabela_sa_parametros,
    "tab-ag-parametros": tabela_ag_parametros,
    "tab-experimento-ag": tabela_experimento_ag,
}


# Figuras


def _curva_mediana(execucoes: list[list[tuple[float, float]]], grade: list[float]) -> list[float]:
    """Mediana, em cada ponto da grade, do valor em degrau de cada execução."""
    curva = []
    for x in grade:
        valores = []
        for pontos in execucoes:
            i = bisect_right([px for px, _ in pontos], x) - 1
            if i >= 0:
                valores.append(pontos[i][1])
        curva.append(statistics.median(valores) if valores else math.nan)
    return curva


def _pontos_por_execucao(linhas: list[Linha], x: str, y: str) -> list[list[tuple[float, float]]]:
    por_execucao = _agrupar(linhas, lambda r: r["execucao"])
    return [sorted((float(r[x]), float(r[y])) for r in grupo) for grupo in por_execucao.values()]


def _grade(execucoes: list[list[tuple[float, float]]], pontos: int = 200) -> list[float]:
    fim = max((p[-1][0] for p in execucoes if p), default=1.0)
    return [fim * (k + 1) / pontos for k in range(pontos)]


def _paineis(n: int):
    fig, eixos = plt.subplots(1, n, figsize=(5 * n, 4), squeeze=False)
    return fig, eixos[0]


def _salvar(fig, caminho: Path) -> Path:
    fig.tight_layout()
    fig.savefig(caminho, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return caminho


def _principais(linhas: list[Linha]) -> list[Linha]:
    algoritmos = set(PRINCIPAIS.values())
    return [
        r
        for r in linhas
        if r["algoritmo"] in algoritmos and r["operador"] == "swap" and r["incremental"] == "1"
    ]


def _nome(algoritmo: str) -> str:
    return next(nome for nome, alg in PRINCIPAIS.items() if alg == algoritmo)


def boxplots(execucoes: list[Linha], caminho: Path) -> Path:
    instancias = _instancias(execucoes)
    fig, eixos = _paineis(len(instancias))
    for ax, instancia in zip(eixos, instancias, strict=True):
        grupos = _agrupar([r for r in execucoes if r["instancia"] == instancia], _rotulo)
        algoritmos = [alg for alg in PRINCIPAIS.values() if alg in grupos]
        ax.boxplot(
            [[float(r["melhor_h"]) for r in grupos[alg]] for alg in algoritmos],
            tick_labels=[_nome(alg) for alg in algoritmos],
        )
        if (ref := REFERENCIAS.get(instancia)) is not None:
            ax.axhline(ref, linestyle="--", color="gray", label=f"referência ({ref})")
            ax.legend(loc="upper right", fontsize=8)
        ax.set_title(EXIBICAO_INSTANCIAS.get(instancia, instancia))
        ax.set_ylabel("melhor h")
    return _salvar(fig, caminho)


def convergencia(historico: list[Linha], series: list[Linha], caminho: Path) -> Path:
    instancias = _instancias(historico)
    fig, eixos = _paineis(len(instancias))
    for ax, instancia in zip(eixos, instancias, strict=True):
        grupos = _agrupar(
            [r for r in historico if r["instancia"] == instancia], lambda r: r["algoritmo"]
        )
        medias = _agrupar(
            [r for r in series if r["instancia"] == instancia and r["serie"] == "media_populacao"],
            lambda r: r["algoritmo"],
        )
        for algoritmo in (alg for alg in PRINCIPAIS.values() if alg in grupos):
            execucoes = _pontos_por_execucao(grupos[algoritmo], "avaliacoes", "melhor_h")
            grade = _grade(execucoes)
            (linha,) = ax.plot(grade, _curva_mediana(execucoes, grade), label=_nome(algoritmo))
            if algoritmo in medias:
                pop = _pontos_por_execucao(medias[algoritmo], "x", "valor")
                ax.plot(
                    grade,
                    _curva_mediana(pop, grade),
                    linestyle="--",
                    color=linha.get_color(),
                    label=f"{_nome(algoritmo)} (média da população)",
                )
        ax.set_yscale("log")
        ax.set_title(EXIBICAO_INSTANCIAS.get(instancia, instancia))
        ax.set_xlabel("avaliações")
        ax.set_ylabel("melhor h (mediana)")
        ax.legend(fontsize=7)
    return _salvar(fig, caminho)


def _curvas_por_instancia(
    series: list[Linha], caminho: Path, xlabel: str, ylabel: str, normalizar: bool
) -> Path:
    fig, ax = plt.subplots(figsize=(6, 4))
    grupos = _agrupar(series, lambda r: r["instancia"])
    for instancia in _instancias(series):
        execucoes = _pontos_por_execucao(grupos[instancia], "x", "valor")
        grade = _grade(execucoes)
        xs = [100 * x / grade[-1] for x in grade] if normalizar else grade
        ax.plot(xs, _curva_mediana(execucoes, grade), label=EXIBICAO_INSTANCIAS.get(instancia))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(fontsize=8)
    return _salvar(fig, caminho)


def _serie(series: list[Linha], algoritmo: str, nome: str) -> list[Linha]:
    return [r for r in _principais(series) if r["algoritmo"] == algoritmo and r["serie"] == nome]


def tratar_resultados(entrada: Path, saida: Path) -> list[Path]:
    execucoes = carregar(entrada, "execucoes")
    historico = carregar(entrada, "historico")
    series = carregar(entrada, "series")
    incremental: list[Linha] = []
    if (arquivo := entrada / "incremental.csv").exists():
        with arquivo.open(newline="") as f:
            incremental = list(csv.DictReader(f))
    saida.mkdir(parents=True, exist_ok=True)

    dados = Dados(execucoes, incremental)
    caminhos = [
        _escrever_tabela(saida / f"{nome}.tex", gerar(dados)) for nome, gerar in TABELAS.items()
    ]
    if execucoes:
        caminhos.append(_escrever_csv(saida / "resumo.csv", resumo(execucoes)))
    if comparacoes := pvalores(execucoes):
        caminhos.append(_escrever_csv(saida / "pvalores.csv", comparacoes))
    if principais := _principais(execucoes):
        caminhos.append(boxplots(principais, saida / "boxplots.png"))
        caminhos.append(
            convergencia(_principais(historico), _principais(series), saida / "convergencia.png")
        )
    if aceitacao := _serie(series, "tempera", "aceitacao"):
        caminhos.append(
            _curvas_por_instancia(
                aceitacao,
                saida / "sa_aceitacao.png",
                "orçamento gasto (%)",
                "taxa de aceitação de pioras (mediana)",
                normalizar=True,
            )
        )
    if diversidade := _serie(series, "genetico", "diversidade"):
        caminhos.append(
            _curvas_por_instancia(
                diversidade,
                saida / "ag_diversidade.png",
                "geração",
                "cromossomos distintos (mediana)",
                normalizar=False,
            )
        )
    return caminhos
