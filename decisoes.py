"""
DECISÕES: regras automáticas da colônia e análise de energia.

Regras (na ordem em que são avaliadas):
  1. Suporte à vida e comunicação ficam SEMPRE ligados (prioridade máxima).
  2. energia < 50 E consumo > 60  -> "ALERTA: reduzir consumo" + MODO ECONOMIA
     (desliga todos os módulos não essenciais).
  3. energia < 50                 -> "AVISO: energia baixa, reduzir consumo"
     (desliga não essenciais, da menor prioridade para a maior, até o
     consumo caber na geração).
  4. consumo > geração            -> equilibra do mesmo jeito da regra 3.
  5. temperatura interna fora de 18 a 26 °C -> ajustar o controle térmico.
  6. equipamento em FALHA         -> alerta de manutenção.
"""

from estruturas import consumidores_nao_essenciais, ids_essenciais

# Limites das regras (kW e °C)
ENERGIA_BAIXA = 50
CONSUMO_ALTO = 60
TEMP_MIN = 18
TEMP_MAX = 26
MARGEM_EQUILIBRIO = 5  # diferença até 5 kW entre geração e consumo = equilíbrio


def consumo_total(consumo):
    """Soma o consumo de todos os módulos (valores do dicionário)."""
    total = 0
    for valor in consumo.values():
        total = total + valor
    return total


def planejar_desligamentos(arvore, consumo, meta):
    """
    Desliga módulos não essenciais, do de menor prioridade para o de maior,
    até o consumo ficar <= meta. Essenciais nunca entram na lista.
    Devolve (lista de nomes desligados, consumo resultante).
    """
    total = consumo_total(consumo)
    desligados = []
    for modulo in consumidores_nao_essenciais(arvore):
        if total <= meta:
            break
        gasto = consumo.get(modulo["id"], 0)
        if gasto > 0:
            desligados.append(f"{modulo['nome']} ({gasto} kW)")
            total = total - gasto
    return desligados, total


def decidir(leitura, arvore):
    """
    Aplica as regras a uma leitura de sensores.
    Devolve a lista de mensagens de decisão, em texto.
    """
    energia = leitura["solar"] + leitura["eolica"]
    consumo = leitura["consumo"]
    total = consumo_total(consumo)
    mensagens = []

    # Regra 1: prioridade ao essencial
    essencial = 0
    for id_modulo in ids_essenciais(arvore):
        essencial = essencial + consumo.get(id_modulo, 0)
    mensagens.append(f"PRIORIDADE: suporte à vida e comunicação LIGADOS ({essencial} kW)")

    # Regras 2, 3 e 4: energia x consumo
    meta = None
    if energia < ENERGIA_BAIXA and total > CONSUMO_ALTO:
        mensagens.append("ALERTA: reduzir consumo")
        mensagens.append("MODO ECONOMIA ativado: desligar todos os não essenciais")
        meta = 0
    elif energia < ENERGIA_BAIXA:
        mensagens.append(f"AVISO: energia baixa ({energia} kW), reduzir consumo")
        meta = energia
    elif total > energia:
        mensagens.append("AVISO: consumo acima da geração, equilibrar")
        meta = energia

    if meta is not None:
        desligados, novo_total = planejar_desligamentos(arvore, consumo, meta)
        if len(desligados) > 0:
            mensagens.append("DESLIGAR: " + ", ".join(desligados))
            mensagens.append(f"Consumo após a ação: {novo_total} kW (antes: {total} kW)")
        else:
            mensagens.append("Nenhum desligamento necessário: consumo já cabe na geração")
        if novo_total > energia:
            falta = novo_total - energia
            mensagens.append(f"ALERTA CRÍTICO: faltam {falta} kW só para os essenciais, usar as baterias")

    # Regra 5: temperatura interna
    if leitura["temp_interna"] < TEMP_MIN:
        mensagens.append(f"AÇÃO: temperatura interna {leitura['temp_interna']} °C, aumentar aquecimento")
    elif leitura["temp_interna"] > TEMP_MAX:
        mensagens.append(f"AÇÃO: temperatura interna {leitura['temp_interna']} °C, aumentar resfriamento")

    # Regra 6: estado dos equipamentos
    for equipamento, estado in leitura["equipamentos"].items():
        if estado != "OK":
            mensagens.append(f"ALERTA: {equipamento} em {estado}, enviar equipe de manutenção")

    return mensagens


def analisar_energia(geracao, consumo):
    """
    Compara geração e consumo do ciclo.
      consumo > geração           -> risco
      geração > consumo + margem  -> possível desperdício
      senão                       -> equilíbrio
    """
    if consumo > geracao:
        return f"ALERTA: consumo maior que geração ({consumo} kW contra {geracao} kW)"
    if geracao - consumo > MARGEM_EQUILIBRIO:
        return f"SUGESTÃO: armazenar energia excedente ({geracao - consumo} kW sobrando)"
    return f"OK: geração e consumo equilibrados ({geracao} kW contra {consumo} kW)"


def avaliar_previsao(geracao_prevista, consumo_atual):
    """Transforma a previsão do próximo ciclo em uma ação antecipada."""
    if geracao_prevista < consumo_atual:
        falta = round(consumo_atual - geracao_prevista, 1)
        return (f"PREVISÃO: déficit de {falta} kW no próximo ciclo, "
                "carregar baterias agora e adiar tarefas não essenciais")
    sobra = round(geracao_prevista - consumo_atual, 1)
    return f"PREVISÃO: geração suficiente no próximo ciclo (sobra de {sobra} kW)"
