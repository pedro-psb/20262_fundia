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
    custo_caminho: int | None
    nos_visitados: int | None
    tempo_s: float


class AnaliseBusca:
    COLUNAS = [campo.name for campo in fields(EstatisticaBusca)]
    ESTATISTICAS_DO_GRAFICO = ["custo_caminho", "nos_visitados", "tempo_s"]
    ROTULOS_DO_GRAFICO = ["Custo do caminho", "Nós visitados", "Tempo (s)"]
    NOME_CSV = "resultados.csv"
    NOME_GRAFICO = "grafico.png"

    def __init__(self, diretorio: Path):
        self.diretorio = diretorio
        self.caminho_csv = diretorio / self.NOME_CSV
        self.caminho_grafico = diretorio / self.NOME_GRAFICO

    def salvar_csv(self, estatisticas: list[EstatisticaBusca]) -> None:
        with self.caminho_csv.open("w", newline="") as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=self.COLUNAS)
            writer.writeheader()
            writer.writerows(asdict(estatistica) for estatistica in estatisticas)

    def salvar_grafico(self, estatisticas: list[EstatisticaBusca]) -> None:
        valores_por_estatistica = {
            nome: [getattr(estatistica, nome) or 0 for estatistica in estatisticas]
            for nome in self.ESTATISTICAS_DO_GRAFICO
        }
        normalizados_por_estatistica = {
            nome: [valor / max(valores) if max(valores) else 0 for valor in valores]
            for nome, valores in valores_por_estatistica.items()
        }

        n_algoritmos = len(estatisticas)
        largura_barra = 0.5 / n_algoritmos
        posicoes_grupo = range(len(self.ESTATISTICAS_DO_GRAFICO))

        fig, ax = plt.subplots(figsize=(8, 5))
        for i, estatistica in enumerate(estatisticas):
            valores = [
                normalizados_por_estatistica[nome][i] for nome in self.ESTATISTICAS_DO_GRAFICO
            ]
            posicoes = [p + i * largura_barra for p in posicoes_grupo]
            ax.bar(posicoes, valores, width=largura_barra, label=estatistica.algoritmo)

        centro_offset = largura_barra * (n_algoritmos - 1) / 2
        ax.set_xticks([p + centro_offset for p in posicoes_grupo])
        ax.set_xticklabels(self.ROTULOS_DO_GRAFICO)
        ax.set_ylabel("Valor normalizado (fração do máximo)")
        ax.set_title("Comparação dos algoritmos de busca")
        ax.legend(title="Algoritmo", loc="center left", bbox_to_anchor=(1, 0.5))

        fig.savefig(self.caminho_grafico, bbox_inches="tight")
        plt.close(fig)

    def executar_analise(self, estatisticas: list[EstatisticaBusca]) -> Path:
        self.diretorio.mkdir(parents=True, exist_ok=True)

        self.salvar_csv(estatisticas)
        self.salvar_grafico(estatisticas)

        return self.diretorio


PROBLEMA = [1, 2, 5, 10]
ALGORITMOS: tuple[type[Busca], ...] = (
    BuscaEmLargura,
    BuscaEmProfundidade,
    BuscaDeCustoUniforme,
    BuscaAEstrela,
)


def coletar_estatisticas(custos_iniciais: list[int]) -> list[EstatisticaBusca]:
    estatisticas = []
    for cls in ALGORITMOS:
        espaco_estado = EspacoEstado(Pessoa.factory(custos_iniciais))
        busca = cls(espaco_estado)
        inicio = time.perf_counter()
        resultado = busca.buscar()
        tempo_s = time.perf_counter() - inicio
        estatisticas.append(
            EstatisticaBusca(
                algoritmo=cls.__name__,
                encontrou_solucao=resultado is not None,
                custo_caminho=resultado.custo_caminho if resultado else None,
                nos_visitados=resultado.nos_visitados if resultado else None,
                tempo_s=tempo_s,
            )
        )
    return estatisticas


def main(diretorio: Path) -> Path:
    estatisticas = coletar_estatisticas(PROBLEMA)
    return AnaliseBusca(diretorio).executar_analise(estatisticas)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("diretorio", type=Path, help="Onde salvar o CSV e o gráfico")
    args = parser.parse_args()

    destino = main(args.diretorio)
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
        assert (diretorio / "grafico.png").exists()

        with caminho_csv.open() as arquivo:
            linhas = list(csv.DictReader(arquivo))
        assert len(linhas) == len(ESTATISTICAS_ESTIMADAS)
        assert linhas[0]["algoritmo"] == "BuscaEmLargura"
        assert linhas[0]["custo_caminho"] == "17"
