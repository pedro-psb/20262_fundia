# Divisão de trabalho

O trabalho é organizado em três etapas, cada uma dependendo da anterior. A etapa 1 (base comum e busca local) libera as duas partes da etapa 2, que correm em paralelo, sem depender uma da outra. A etapa 3 (integração) só começa quando ambas estiverem prontas.

```text
 Etapa 1                Etapa 2           Etapa 3
 (bloqueia)             (em paralelo)     (todos juntos)

                       +--> SAN --+
                       |          |
    BAS ----> BLO -----+          +----->   INT
                       |          |
                       +--> GEN --+

Etapa 1  base comum e busca local, que valida h e o resto da base na pratica
Etapa 2  partes independentes, cada uma com seu codigo e suas secoes do relatorio
Etapa 3  rodada final, resultados, discussao e revisao

BAS  base comum (Pedro)
BLO  busca local (Pedro)
SAN  simulated annealing e analise (Paulo)
GEN  algoritmo genetico (Diogo)
INT  integracao (todos)
```

## Etapa 1 — base comum e busca local (Pedro)

**BAS: base comum**

- **Código:** leitura das instâncias e `h(π)`; interface do problema; operadores swap, insertion e 2-opt; contador de avaliações com orçamento; runner de experimentos; busca aleatória como algoritmo de referência.
- **Testes:**
  - `tests/test_base.py`
    - `h` da identidade na instância pequena = 4366
    - exemplo da Fig. 1: `h` = 39 e ótimo = 22
    - cada operador gera permutações válidas
    - cada operador gera o número esperado de sucessores
    - orçamento para exatamente em `B`
    - histórico registra cada melhora
    - runner salva e relê os CSVs no formato comum
- **Relatório:**
  - `docs/metodologia.tex`: Metodologia, com as tabelas fixas (interface, tamanho das vizinhanças, instâncias) e a saída da verificação de `h`
- **Artefatos:**
  - `docs/resultados/<algoritmo>_execucoes.csv` e `docs/resultados/<algoritmo>_historico.csv`: formato comum escrito pelo runner (uma linha por execução; melhor `h` × avaliações)
  - `docs/resultados/aleatoria_*.csv`: busca aleatória, para validar o formato
  - Reproduzível com `make resultado-aleatoria`

**BLO: busca local**

- **Código:** greedy descent com random restart (2+ variantes); avaliação incremental; comparação das vizinhanças.
- **Testes:**
  - `tests/test_busca_local.py`
    - descida termina em ótimo local
    - cada variante respeita o orçamento
    - avaliação incremental igual à completa em movimentos aleatórios
- **Relatório:**
  - `docs/busca-local.tex`: Greedy Descent
  - `docs/anexos.tex`: bloco de busca local
- **Artefatos:**
  - `docs/resultados/busca_local_*.csv`: execuções e histórico, com passos, restarts e ótimos locais por execução
  - `docs/resultados/vizinhancas.csv`: comparação das vizinhanças
  - `docs/resultados/incremental.csv`: tempos da avaliação completa × incremental
  - Reproduzível com `make resultado-local`

## Etapa 2 — partes em paralelo

**SAN: simulated annealing e análise (Paulo)**

- **Código:** simulated annealing com calibração automática; pipeline de análise que lê os CSVs e gera tabelas e figuras.
- **Testes:**
  - `tests/test_tempera.py`
    - calibração dá `T0 > Tf`
    - resfriamento termina em `B`
    - aceitação de pioras perto de 1 com `T` alta e perto de 0 com `T` baixa
  - `tests/test_analise.py`
    - pipeline roda com CSVs sintéticos e gera todas as tabelas e figuras
- **Relatório:**
  - `docs/tempera.tex`: Simulated Annealing
  - `docs/comparacao.tex`: comparação dos algoritmos
  - `docs/anexos.tex`: bloco de SA
- **Artefatos:**
  - `docs/resultados/tempera_*.csv`: execuções e histórico, com os parâmetros calibrados por execução
  - `docs/resultados/tempera_aceitacao.csv`: taxa de aceitação de pioras ao longo da execução
  - Reproduzível com `make resultado-tempera`

**GEN: algoritmo genético (Diogo)**

- **Código:** algoritmo genético (seleção, OX/PMX, mutação, elitismo); medida de diversidade; experimento adicional sobre a recombinação.
- **Testes:**
  - `tests/test_genetico.py`
    - cruzamento e mutação geram permutações válidas
    - exemplo de cruzamento do relatório bate com o código
    - orçamento respeitado com a última geração incompleta
- **Relatório:**
  - `docs/genetico.tex`: Algoritmo Genético
  - `docs/anexos.tex`: bloco de AG
- **Artefatos:**
  - `docs/resultados/genetico_*.csv`: execuções e histórico, com a média da população
  - `docs/resultados/genetico_diversidade.csv`: diversidade por geração
  - `docs/resultados/genetico_experimento.csv`: experimento adicional
  - Reproduzível com `make resultado-genetico`

## Etapa 3 — INT: integração (todos)

- **Código:** congelado; só a configuração da rodada final, incluindo a vizinhança escolhida pela comparação do BLO (T2) no SA e na busca local.
- **Testes:**
  - `tests/`: todos passando no código congelado, junto com o lint
  - Rodada de fumaça: taxa de aceitação do SA continua adequada com a vizinhança escolhida
- **Relatório:**
  - `docs/discussao.tex`: discussão (ótimos locais, exploração × intensificação, efeito da escala, quando o AG compensa)
  - `docs/*.tex`: números finais; revisão cruzada
  - `docs/intro.tex`, `docs/conclusao.tex`, `docs/abstract.tex`: introdução, conclusão e resumo (Pedro)
- **Artefatos:**
  - `docs/resultados/*.csv`: dados da rodada final, versionados
  - `docs/results/*.png`: todas as figuras, geradas pelo pipeline de análise a partir dos CSVs (taxa de aceitação, diversidade, boxplots, convergência)
  - `docs/*.tex`: todas as tabelas preenchidas com os números dos CSVs
  - `README.md`: tabela de Reprodução completa
  - Reproduzível com `make resultado-todos` (todos os CSVs) e `make resultado-figuras` (figuras)

## Critério de "pronto"

- Testes e lint passando.
- Roda pelo runner e gera seus CSVs.
- Toda tabela e figura reproduzível por um comando listado em [Reprodução](README.md#reprodução).
- Código e texto revisados por outro membro via PR (Diogo revisa SAN, Paulo revisa BLO, Pedro revisa GEN).
