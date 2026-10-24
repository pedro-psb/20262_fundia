"""Pipeline de análise."""

from tp2.analise import TABELAS, tratar_resultados
from tp2.experimento import Configuracao, executar, salvar


def test_pipeline_com_csvs_sinteticos(tmp_path):
    brutos, saida = tmp_path / "brutos", tmp_path / "saida"
    resultados = [
        executar(Configuracao(algoritmo, instancia, e, orcamento=3000))
        for algoritmo in ("gd-best", "tempera", "genetico")
        for instancia in ("pequena", "media")
        for e in range(3)
    ]
    salvar(resultados, brutos)

    caminhos = tratar_resultados(brutos, saida)

    nomes = {c.name for c in caminhos}
    assert nomes == {f"{t}.tex" for t in TABELAS} | {
        "resumo.csv",
        "pvalores.csv",
        "boxplots.png",
        "convergencia.png",
        "sa_aceitacao.png",
        "ag_diversidade.png",
    }
    assert all(c.stat().st_size > 0 for c in caminhos)
    principal = (saida / "tab-principal.tex").read_text()
    assert "GD+RR" in principal
    assert principal.count(r"\midrule") == 2


def test_sem_dados_gera_tabelas_vazias(tmp_path):
    caminhos = tratar_resultados(tmp_path / "vazio", tmp_path / "saida")

    assert {c.name for c in caminhos} == {f"{t}.tex" for t in TABELAS}
    assert "--" in (tmp_path / "saida" / "tab-incremental.tex").read_text()
