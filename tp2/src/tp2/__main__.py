import argparse
from pathlib import Path

from tp2.algoritmos import ALGORITMOS
from tp2.problema import NOMES_INSTANCIAS, OPERADORES

BRUTOS = Path("docs/results/raw")
FINAIS = Path("docs/results/final")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="tp2", description="TP2 - Fundamentos de IA")
    comandos = parser.add_subparsers(dest="comando", required=True)

    run = comandos.add_parser("run", help="roda um algoritmo e grava os CSVs brutos")
    run.add_argument(
        "algoritmo",
        choices=[*ALGORITMOS, "verificar", "incremental"],
        help="'verificar' imprime os valores de verificação de h; "
        "'incremental' mede o tempo da avaliação completa × incremental",
    )
    run.add_argument(
        "-i",
        "--instancia",
        action="append",
        help="nome (pequena, media, grande) ou caminho; repetível (padrão: todas)",
    )
    run.add_argument("-o", "--saida", type=Path, default=BRUTOS)
    run.add_argument("--operador", choices=list(OPERADORES), default="swap")
    run.add_argument("--sem-incremental", action="store_true")
    run.add_argument("--execucoes", type=int, help="padrão: 30/30/10 conforme a instância")
    run.add_argument("--orcamento", type=int, help="padrão: 50k/150k/300k conforme a instância")
    run.add_argument("-j", "--processos", type=int, help="padrão: número de CPUs")

    tratar = comandos.add_parser(
        "tratar-resultados", help="gera as tabelas e figuras do relatório a partir dos CSVs brutos"
    )
    tratar.add_argument("entrada", type=Path, nargs="?", default=BRUTOS)
    tratar.add_argument("-o", "--saida", type=Path, default=FINAIS)

    args = parser.parse_args(argv)

    if args.comando == "tratar-resultados":
        from tp2.analise import tratar_resultados

        caminhos = tratar_resultados(args.entrada, args.saida)
    else:
        from tp2 import experimento

        instancias = args.instancia or list(NOMES_INSTANCIAS)
        if args.algoritmo == "verificar":
            print(experimento.verificar())
            return
        if args.algoritmo == "incremental":
            caminhos = [experimento.medir_incremental(instancias, args.saida)]
        else:
            caminhos = experimento.rodar(
                args.algoritmo,
                instancias,
                args.saida,
                operador=args.operador,
                incremental=not args.sem_incremental,
                execucoes=args.execucoes,
                orcamento=args.orcamento,
                processos=args.processos,
            )
    for caminho in caminhos:
        print(f"salvo: {caminho}")


if __name__ == "__main__":
    main()
