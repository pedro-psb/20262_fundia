import argparse
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.style.use(["seaborn-v0_8-whitegrid", "seaborn-v0_8-muted"])

# Dados fictícios, apenas para exercitar a geração dos gráficos.
# Substitua pelas métricas reais coletadas no TP2.
CATEGORIAS = ["Método A", "Método B", "Método C", "Método D"]
VALORES = [12.0, 7.5, 15.2, 9.8]


def salvar_grafico_barras(caminho: Path) -> Path:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    barras = ax.bar(CATEGORIAS, VALORES, width=0.55)
    ax.bar_label(barras, fmt="%.1f", padding=3, fontsize=9)
    ax.set_title("Gráfico de Barras (exemplo)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Métrica (unidade)")
    ax.set_ylim(0, max(VALORES) * 1.15)
    fig.tight_layout()
    fig.savefig(caminho, bbox_inches="tight")
    plt.close(fig)
    return caminho


def salvar_grafico_linhas(caminho: Path) -> Path:
    xs = list(range(50))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for i, categoria in enumerate(CATEGORIAS):
        ax.plot(xs, [math.log1p(x) * (i + 1) for x in xs], label=categoria)
    ax.set_title("Gráfico de Linhas (exemplo)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Iteração")
    ax.set_ylabel("Métrica (unidade)")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(caminho, bbox_inches="tight")
    plt.close(fig)
    return caminho


def main(diretorio: Path) -> list[Path]:
    diretorio.mkdir(parents=True, exist_ok=True)
    return [
        salvar_grafico_barras(diretorio / "grafico_barras.png"),
        salvar_grafico_linhas(diretorio / "grafico_linhas.png"),
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("docs/results"),
        help="Diretório onde salvar os gráficos (padrão: docs/results)",
    )
    args = parser.parse_args()

    for caminho in main(args.output):
        print(f"Gráfico salvo em: {caminho}")


# Testes


class TestAnalise:
    def test_main_gera_graficos(self, tmp_path):
        caminhos = main(tmp_path / "results")
        assert len(caminhos) == 2
        for caminho in caminhos:
            assert caminho.exists()
