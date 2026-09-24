import argparse


def main() -> None:
    """Ponto de entrada do TP2. Substitua pela implementação do trabalho."""
    print("TP2: implementação pendente.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TP2 - Fundamentos de IA")
    parser.parse_args()
    main()


# Testes


class TestMain:
    def test_main_executa(self, capsys):
        main()
        assert "TP2" in capsys.readouterr().out
