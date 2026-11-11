"""
DADOS da colônia Aurora Siger.

Este arquivo guarda apenas dados (nenhuma regra de decisão):
  1. séries históricas em LISTAS, usadas para treinar a regressão;
  2. a HIERARQUIA de sistemas, em forma de árvore (cada nó é um dicionário);
  3. as leituras dos sensores, uma por ciclo, como DICIONÁRIOS (chave-valor).

Os valores são fictícios e didáticos. Unidade de energia: kW (média do ciclo).
"""

# ---------------------------------------------------------------------------
# 1. Séries históricas (listas paralelas: a posição i de uma combina com a
#    posição i da outra)
# ---------------------------------------------------------------------------

# Exemplo do enunciado: vento (m/s) x energia eólica gerada (kW)
historico_vento = [8, 10, 12]
historico_energia_eolica = [20, 25, 30]

# Irradiância solar (W/m²) x energia solar gerada (kW)
historico_irradiancia = [200, 400, 600, 800]
historico_energia_solar = [10, 21, 29, 41]

# ---------------------------------------------------------------------------
# 2. Hierarquia de sistemas (árvore)
#    - nós internos têm "filhos";
#    - folhas consumidoras têm "id", "essencial" e "prioridade"
#      (prioridade 1 = a primeira a ser desligada quando falta energia);
#    - folhas geradoras têm "id" e "tipo": "gerador".
# ---------------------------------------------------------------------------

colonia = {
    "nome": "Colônia Aurora Siger",
    "filhos": [
        {
            "nome": "Sistema energético",
            "filhos": [
                {"nome": "Solar", "filhos": [
                    {"nome": "Painel solar A", "id": "painel_solar_A", "tipo": "gerador"},
                    {"nome": "Painel solar B", "id": "painel_solar_B", "tipo": "gerador"},
                ]},
                {"nome": "Eólico", "filhos": [
                    {"nome": "Turbina eólica 1", "id": "turbina_eolica_1", "tipo": "gerador"},
                ]},
                {"nome": "Baterias", "id": "baterias", "tipo": "armazenamento"},
            ],
        },
        {
            "nome": "Suporte à vida",
            "filhos": [
                {"nome": "Gerador de oxigênio", "id": "oxigenio", "essencial": True, "prioridade": 10},
                {"nome": "Reciclagem de água", "id": "agua", "essencial": True, "prioridade": 9},
                {"nome": "Controle térmico", "id": "controle_termico", "essencial": True, "prioridade": 9},
            ],
        },
        {
            "nome": "Comunicação",
            "filhos": [
                {"nome": "Antena Terra-Marte", "id": "comunicacao", "essencial": True, "prioridade": 8},
            ],
        },
        {
            "nome": "Produção",
            "filhos": [
                {"nome": "Estufa", "id": "estufa", "essencial": False, "prioridade": 4},
                {"nome": "Laboratório", "id": "laboratorio", "essencial": False, "prioridade": 3},
                {"nome": "Oficina de mineração", "id": "oficina", "essencial": False, "prioridade": 1},
            ],
        },
        {
            "nome": "Habitação",
            "filhos": [
                {"nome": "Iluminação das áreas comuns", "id": "iluminacao", "essencial": False, "prioridade": 2},
            ],
        },
    ],
}

# ---------------------------------------------------------------------------
# 3. Leituras dos sensores (lista de dicionários, uma leitura por ciclo)
#    - "solar" e "eolica": geração medida no ciclo (kW)
#    - "consumo": dicionário módulo -> consumo medido (kW)
#    - "equipamentos": dicionário equipamento -> "OK" ou "FALHA"
#    - "previsao_vento" e "previsao_irradiancia": previsão meteorológica
#      para o PRÓXIMO ciclo, usada pelo modelo de regressão
# ---------------------------------------------------------------------------

def _equipamentos(turbina="OK"):
    """Estado padrão dos equipamentos (só a turbina varia nos cenários)."""
    return {
        "painel_solar_A": "OK",
        "painel_solar_B": "OK",
        "turbina_eolica_1": turbina,
        "baterias": "OK",
    }


leituras = [
    {
        "ciclo": 1, "descricao": "Manhã estável",
        "solar": 30, "eolica": 25, "vento": 10, "irradiancia": 600,
        "temp_interna": 21, "temp_externa": -45,
        "consumo": {"oxigenio": 10, "agua": 6, "controle_termico": 8, "comunicacao": 4,
                    "laboratorio": 12, "estufa": 8, "iluminacao": 3, "oficina": 1},
        "equipamentos": _equipamentos(),
        "previsao_vento": 13, "previsao_irradiancia": 100,  # tempestade se aproximando
    },
    {
        "ciclo": 2, "descricao": "Tempestade de poeira",
        "solar": 8, "eolica": 32, "vento": 13, "irradiancia": 100,
        "temp_interna": 20, "temp_externa": -60,
        "consumo": {"oxigenio": 10, "agua": 6, "controle_termico": 10, "comunicacao": 4,
                    "laboratorio": 14, "estufa": 10, "iluminacao": 6, "oficina": 10},
        "equipamentos": _equipamentos(),
        "previsao_vento": 12, "previsao_irradiancia": 800,
    },
    {
        "ciclo": 3, "descricao": "Pico de geração",
        "solar": 45, "eolica": 35, "vento": 14, "irradiancia": 850,
        "temp_interna": 22, "temp_externa": -20,
        "consumo": {"oxigenio": 10, "agua": 6, "controle_termico": 6, "comunicacao": 4,
                    "laboratorio": 0, "estufa": 4, "iluminacao": 0, "oficina": 0},
        "equipamentos": _equipamentos(),
        "previsao_vento": 8, "previsao_irradiancia": 0,  # noite
    },
    {
        "ciclo": 4, "descricao": "Noite fria",
        "solar": 0, "eolica": 20, "vento": 8, "irradiancia": 0,
        "temp_interna": 16, "temp_externa": -85,
        "consumo": {"oxigenio": 10, "agua": 6, "controle_termico": 14, "comunicacao": 4,
                    "laboratorio": 0, "estufa": 8, "iluminacao": 3, "oficina": 0},
        "equipamentos": _equipamentos(),
        "previsao_vento": 12, "previsao_irradiancia": 700,
    },
    {
        "ciclo": 5, "descricao": "Falha na turbina eólica",
        "solar": 38, "eolica": 0, "vento": 12, "irradiancia": 750,
        "temp_interna": 22, "temp_externa": -30,
        "consumo": {"oxigenio": 10, "agua": 6, "controle_termico": 8, "comunicacao": 4,
                    "laboratorio": 12, "estufa": 0, "iluminacao": 0, "oficina": 8},
        "equipamentos": _equipamentos(turbina="FALHA"),
        "previsao_vento": 11, "previsao_irradiancia": 800,
    },
    {
        "ciclo": 6, "descricao": "Tarde quente no laboratório",
        "solar": 42, "eolica": 22, "vento": 9, "irradiancia": 800,
        "temp_interna": 28, "temp_externa": -15,
        "consumo": {"oxigenio": 10, "agua": 6, "controle_termico": 12, "comunicacao": 4,
                    "laboratorio": 14, "estufa": 8, "iluminacao": 3, "oficina": 3},
        "equipamentos": _equipamentos(),
        "previsao_vento": 7, "previsao_irradiancia": 300,  # fim de tarde
    },
]
