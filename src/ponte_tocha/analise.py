import argparse
import csv
import time
from dataclasses import asdict, dataclass, fields
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ponte_tocha.base import EspacoEstado, Pessoa  # noqa: E402
from ponte_tocha.busca import (  # noqa: E402
    Busca,
    BuscaAEstrela,
    BuscaDeCustoUniforme,
    BuscaEmLargura,
    BuscaEmProfundidade,
)

plt.style.use(["seaborn-v0_8-whitegrid", "seaborn-v0_8-muted"])


@dataclass(frozen=True)
class EstatisticaBusca:
    """Métricas de uma execução de busca, usadas para comparar os algoritmos."""

    algoritmo: str
    encontrou_solucao: bool
    custo_caminho: float | None
    nos_visitados: float | None
    tempo_s: float
    n_repeticoes: int = 1


@dataclass(frozen=True)
class ConfigGrafico:
    campo: str
    nome_arquivo: str
    titulo: str
    ylabel: str
    formato_valor: str
    linha_referencia: float | None = None
    rotulo_referencia: str | None = None
    multiplicador: float = 1.0


class AnaliseBusca:
    COLUNAS = [campo.name for campo in fields(EstatisticaBusca)]
    NOME_CSV = "resultados.csv"

    CONFIGURACOES_GRAFICOS: tuple[ConfigGrafico, ...] = (
        ConfigGrafico(
            campo="custo_caminho",
            nome_arquivo="grafico_custo.png",
            titulo="Custo do Caminho (Tempo Total de Travessia)",
            ylabel="Tempo de travessia (minutos)",
            formato_valor="%.1f",
            linha_referencia=17.0,
            rotulo_referencia="Mínimo teórico (17 min)",
        ),
        ConfigGrafico(
            campo="nos_visitados",
            nome_arquivo="grafico_nos_visitados.png",
            titulo="Nós Visitados durante a Busca",
            ylabel="Quantidade de nós visitados",
            formato_valor="%.1f",
        ),
        ConfigGrafico(
            campo="tempo_s",
            nome_arquivo="grafico_tempo.png",
            titulo="Tempo de Processamento",
            ylabel="Tempo de processamento (ms)",
            formato_valor="%.3f",
            multiplicador=1000.0,
        ),
    )

    def __init__(self, diretorio: Path):
        self.diretorio = diretorio
        self.caminho_csv = diretorio / self.NOME_CSV

    def salvar_csv(self, estatisticas: list[EstatisticaBusca]) -> None:
        with self.caminho_csv.open("w", newline="") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=self.COLUNAS)
            writer.writeheader()
            writer.writerows(asdict(estatistica) for estatistica in estatisticas)

    def salvar_graficos(self, estatisticas: list[EstatisticaBusca]) -> list[Path]:
        caminhos_gerados = []
        algoritmos = [e.algoritmo for e in estatisticas]
        cores = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]

        for config in self.CONFIGURACOES_GRAFICOS:
            valores = [(getattr(e, config.campo) or 0) * config.multiplicador for e in estatisticas]
            caminho_arquivo = self.diretorio / config.nome_arquivo

            fig, ax = plt.subplots(figsize=(7, 4.5))
            barras = ax.bar(
                algoritmos,
                valores,
                color=cores[: len(algoritmos)],
                width=0.55,
            )
            ax.set_ylabel(config.ylabel)
            ax.set_title(config.titulo, fontsize=12, fontweight="bold")
            ax.tick_params(axis="x", rotation=15)

            if config.linha_referencia is not None:
                ax.axhline(
                    y=config.linha_referencia * config.multiplicador,
                    color="gray",
                    linestyle="--",
                    linewidth=1.5,
                    alpha=0.85,
                    label=config.rotulo_referencia or f"{config.linha_referencia}",
                )
                ax.legend(loc="upper right")

            labels = [
                config.formato_valor % val if getattr(e, config.campo) is not None else "N/A"
                for val, e in zip(valores, estatisticas, strict=False)
            ]
            ax.bar_label(barras, labels=labels, padding=3, fontsize=9)

            ref_val = (
                [config.linha_referencia * config.multiplicador]
                if config.linha_referencia is not None
                else []
            )
            max_y = max(valores + ref_val)
            if max_y > 0:
                ax.set_ylim(0, max_y * 1.15)

            fig.tight_layout()
            fig.savefig(caminho_arquivo, bbox_inches="tight")
            plt.close(fig)
            caminhos_gerados.append(caminho_arquivo)

        return caminhos_gerados

    def salvar_grafico(self, estatisticas: list[EstatisticaBusca]) -> None:
        """Mantido para compatibilidade com chamadas legadas."""
        self.salvar_graficos(estatisticas)

    def executar_analise(self, estatisticas: list[EstatisticaBusca]) -> Path:
        self.diretorio.mkdir(parents=True, exist_ok=True)

        self.salvar_csv(estatisticas)
        self.salvar_graficos(estatisticas)

        return self.diretorio


PROBLEMA = [1, 2, 5, 10]
ALGORITMOS: tuple[type[Busca], ...] = (
    BuscaEmLargura,
    BuscaEmProfundidade,
    BuscaDeCustoUniforme,
    BuscaAEstrela,
)


def coletar_estatisticas(
    custos_iniciais: list[int],
    n_repeticoes: int = 100,
) -> list[EstatisticaBusca]:
    estatisticas = []
    for cls in ALGORITMOS:
        tempos: list[float] = []
        custos: list[int] = []
        nos_visitados_lista: list[int] = []
        solucoes_encontradas = 0

        for _ in range(n_repeticoes):
            espaco_estado = EspacoEstado(list(Pessoa.factory(custos_iniciais)))
            busca = cls(espaco_estado)
            inicio = time.perf_counter()
            resultado = busca.buscar()
            tempo_s = time.perf_counter() - inicio
            tempos.append(tempo_s)

            if resultado is not None:
                solucoes_encontradas += 1
                custos.append(resultado.custo_caminho)
                nos_visitados_lista.append(resultado.nos_visitados)

        encontrou_solucao = solucoes_encontradas > 0
        custo_medio = sum(custos) / len(custos) if custos else None
        nos_visitados_medio = (
            sum(nos_visitados_lista) / len(nos_visitados_lista) if nos_visitados_lista else None
        )
        tempo_medio = sum(tempos) / len(tempos) if tempos else 0.0

        estatisticas.append(
            EstatisticaBusca(
                algoritmo=cls.__name__,
                encontrou_solucao=encontrou_solucao,
                custo_caminho=round(custo_medio, 2) if custo_medio is not None else None,
                nos_visitados=round(nos_visitados_medio, 2)
                if nos_visitados_medio is not None
                else None,
                tempo_s=tempo_medio,
                n_repeticoes=n_repeticoes,
            )
        )
    return estatisticas


def main(diretorio: Path, n_repeticoes: int = 100) -> Path:
    estatisticas = coletar_estatisticas(PROBLEMA, n_repeticoes=n_repeticoes)
    return AnaliseBusca(diretorio).executar_analise(estatisticas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("diretorio", type=Path, help="Onde salvar o CSV e o gráfico")
    parser.add_argument(
        "--repeticoes",
        "-n",
        type=int,
        default=100,
        help="Número de repetições por algoritmo (padrão: 100)",
    )
    args = parser.parse_args()

    destino = main(args.diretorio, n_repeticoes=args.repeticoes)
    print(f"Resultados salvos em: {destino}")


# Testes

DIRETORIO_TESTE = Path("/tmp/ponte_tocha_analise")

# Valores estimados a mao, so para exercitar executar_analise sem depender
# dos algoritmos de busca implementados.
ESTATISTICAS_ESTIMADAS = [
    EstatisticaBusca(
        algoritmo="BuscaEmLargura",
        encontrou_solucao=True,
        custo_caminho=17,
        nos_visitados=15,
        tempo_s=0.0005,
    ),
    EstatisticaBusca(
        algoritmo="BuscaEmProfundidade",
        encontrou_solucao=True,
        custo_caminho=23,
        nos_visitados=10,
        tempo_s=0.0003,
    ),
    EstatisticaBusca(
        algoritmo="BuscaDeCustoUniforme",
        encontrou_solucao=True,
        custo_caminho=17,
        nos_visitados=20,
        tempo_s=0.0008,
    ),
    EstatisticaBusca(
        algoritmo="BuscaAEstrela",
        encontrou_solucao=True,
        custo_caminho=17,
        nos_visitados=12,
        tempo_s=0.0006,
    ),
]


class TestExecutarAnalise:
    def test_executar_analise_com_valores_estimados(self):
        diretorio = AnaliseBusca(DIRETORIO_TESTE).executar_analise(ESTATISTICAS_ESTIMADAS)
        print(f"\nResultados da analise em: {diretorio}")

        caminho_csv = diretorio / "resultados.csv"
        assert caminho_csv.exists()
        assert (diretorio / "grafico_custo.png").exists()
        assert (diretorio / "grafico_nos_visitados.png").exists()
        assert (diretorio / "grafico_tempo.png").exists()

        with caminho_csv.open() as arquivo:
            linhas = list(csv.DictReader(arquivo))
        assert len(linhas) == len(ESTATISTICAS_ESTIMADAS)
        assert linhas[0]["algoritmo"] == "BuscaEmLargura"
        assert linhas[0]["custo_caminho"] == "17"

    def test_coletar_estatisticas_com_repeticoes(self):
        estatisticas = coletar_estatisticas([1, 2], n_repeticoes=5)
        assert len(estatisticas) == len(ALGORITMOS)
        for stat in estatisticas:
            assert stat.encontrou_solucao is True
            assert stat.n_repeticoes == 5
            assert stat.custo_caminho is not None
            assert stat.nos_visitados is not None
            assert stat.tempo_s > 0
