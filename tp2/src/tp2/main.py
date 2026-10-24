import argparse
from pathlib import Path


def main(diretorio: Path) -> list[Path]:
    """Gera as tabelas e figuras do relatório a partir dos CSVs em docs/resultados."""
    diretorio.mkdir(parents=True, exist_ok=True)
    return []


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
