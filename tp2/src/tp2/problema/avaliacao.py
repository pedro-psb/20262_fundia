"""Função de avaliação h, memo da recursão de C e heurística gulosa."""

from .instancia import Instancia


def h(inst: Instancia, perm: list[int]) -> int:
    """Atraso ponderado total, calculado do zero."""
    return h_sufixo(inst, perm, 0, [], [])


def h_sufixo(
    inst: Instancia, perm: list[int], k: int, conclusao: list[int], custo: list[int]
) -> int:
    """h de `perm` recalculando só a partir da posição `k`.

    `conclusao` e `custo` são o memo da recursão de C (e do custo acumulado) de uma
    permutação que coincide com `perm` nas posições antes de `k`.
    """
    t, p, d, w = inst.t, inst.p, inst.d, inst.w
    c = conclusao[k - 1] if k else 0
    total = custo[k - 1] if k else 0
    anterior = perm[k - 1] if k else 0
    for j in perm[k:]:
        c += t[anterior][j] + p[j]
        if c > d[j]:
            total += w[j] * (c - d[j])
        anterior = j
    return total


def estender(
    inst: Instancia, perm: list[int], k: int, conclusao: list[int], custo: list[int]
) -> tuple[list[int], list[int]]:
    """Memo da recursão de C e do custo acumulado, por posição de `perm`.

    As posições antes de `k` são copiadas de `conclusao` e `custo`; só o sufixo é recalculado.
    """
    t, p, d, w = inst.t, inst.p, inst.d, inst.w
    novo_c, novo_custo = conclusao[:k], custo[:k]
    c = novo_c[-1] if k else 0
    total = novo_custo[-1] if k else 0
    anterior = perm[k - 1] if k else 0
    for j in perm[k:]:
        c += t[anterior][j] + p[j]
        if c > d[j]:
            total += w[j] * (c - d[j])
        novo_c.append(c)
        novo_custo.append(total)
        anterior = j
    return novo_c, novo_custo


def cronograma(inst: Instancia, perm: list[int]) -> tuple[list[int], list[int]]:
    return estender(inst, perm, 0, [], [])


def guloso(inst: Instancia) -> list[int]:
    """Escolhe sempre o ativo de menor acréscimo imediato de atraso ponderado.

    Empates (comuns no início, quando nada atrasa) vão para o ativo mais próximo.
    """
    t, p, d, w = inst.t, inst.p, inst.d, inst.w
    restantes = set(range(1, inst.n + 1))
    anterior = conclusao = 0
    perm = []

    def chave(j: int) -> tuple[int, int, int]:
        cj = conclusao + t[anterior][j] + p[j]
        return (w[j] * max(0, cj - d[j]), t[anterior][j], j)

    while restantes:
        j = min(restantes, key=chave)
        conclusao += t[anterior][j] + p[j]
        anterior = j
        restantes.remove(j)
        perm.append(j)
    return perm
