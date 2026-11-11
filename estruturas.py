"""
ESTRUTURAS: funções para navegar na árvore de sistemas e montar o índice
chave-valor (tabela hash) a partir dela.

A árvore guarda a hierarquia (quem pertence a quem). O índice é um
dicionário id -> nó: o Python calcula o hash da chave e encontra o nó em
tempo médio O(1), sem percorrer a árvore inteira.
"""


def eh_folha(no):
    """Uma folha é um nó sem filhos."""
    return "filhos" not in no or len(no["filhos"]) == 0


def listar_arvore(no, nivel=0):
    """Devolve a árvore como linhas de texto indentadas (percurso recursivo)."""
    marcador = "" if nivel == 0 else "  " * (nivel - 1) + "└─ "
    detalhe = ""
    if "essencial" in no:
        detalhe = " [essencial]" if no["essencial"] else f" [não essencial, prioridade {no['prioridade']}]"
    elif no.get("tipo") in ("gerador", "armazenamento"):
        detalhe = f" [{no['tipo']}]"
    linhas = [marcador + no["nome"] + detalhe]
    if not eh_folha(no):
        for filho in no["filhos"]:
            linhas = linhas + listar_arvore(filho, nivel + 1)
    return linhas


def buscar_por_caminho(raiz, caminho):
    """
    Navega da raiz até um subsistema seguindo os nomes do caminho.
    Exemplo: buscar_por_caminho(colonia, ["Sistema energético", "Solar"]).
    Devolve o nó encontrado ou None.
    """
    atual = raiz
    for nome in caminho:
        proximo = None
        if not eh_folha(atual):
            for filho in atual["filhos"]:
                if filho["nome"] == nome:
                    proximo = filho
        if proximo is None:
            return None
        atual = proximo
    return atual


def coletar_folhas(no):
    """Devolve a lista de todas as folhas abaixo de um nó (recursivo)."""
    if eh_folha(no):
        return [no]
    folhas = []
    for filho in no["filhos"]:
        folhas = folhas + coletar_folhas(filho)
    return folhas


def construir_indice(raiz):
    """Monta o dicionário id -> nó com todas as folhas que têm id."""
    indice = {}
    for folha in coletar_folhas(raiz):
        if "id" in folha:
            indice[folha["id"]] = folha
    return indice


def consumidores_nao_essenciais(raiz):
    """Lista os módulos não essenciais, do primeiro ao último a ser desligado."""
    lista = []
    for folha in coletar_folhas(raiz):
        if folha.get("essencial") is False:
            lista.append(folha)
    # insertion sort por prioridade crescente (menor prioridade sai primeiro)
    for i in range(1, len(lista)):
        atual = lista[i]
        j = i - 1
        while j >= 0 and lista[j]["prioridade"] > atual["prioridade"]:
            lista[j + 1] = lista[j]
            j = j - 1
        lista[j + 1] = atual
    return lista


def ids_essenciais(raiz):
    """Devolve os ids dos módulos essenciais (suporte à vida e comunicação)."""
    ids = []
    for folha in coletar_folhas(raiz):
        if folha.get("essencial") is True:
            ids.append(folha["id"])
    return ids
