# Sistema Inteligente da Colônia Aurora Siger — Fase 3

Atividade integradora da Fase 3 (FIAP, Ciência da Computação, 1CCOS 2026/2).

A colônia em Marte não pode esperar ordens da Terra (a latência chega a mais de 20 minutos).
Este sistema lê os sensores de energia, clima, consumo e equipamentos e **decide sozinho**
o que fazer. Ele também **prevê a geração do próximo ciclo**, para agir antes de faltar energia.
Assim, deixa de só reagir a problemas e passa a antecipá-los.

Python puro, sem bibliotecas externas.

## Como executar

```bash
python3 main.py     # roda a simulação completa (6 ciclos)
python3 testes.py   # confere os exemplos do enunciado
```

## Organização do código

Dados, lógica e decisões ficam em arquivos separados:

| Arquivo | Papel | O que tem |
|---|---|---|
| [`dados.py`](dados.py) | **Dados** | Séries históricas em listas, árvore de sistemas, leituras dos sensores em dicionários |
| [`estruturas.py`](estruturas.py) | **Lógica de acesso** | Navegação na árvore (recursiva), índice chave-valor, ordem de desligamento |
| [`previsao.py`](previsao.py) | **Modelo** | Regressão linear simples à mão (mínimos quadrados), R², previsão de geração |
| [`decisoes.py`](decisoes.py) | **Decisões** | Regras automáticas e análise de energia |
| [`main.py`](main.py) | Execução | Junta tudo e imprime o relatório da simulação |
| [`testes.py`](testes.py) | Testes | Exemplos do enunciado transformados em `assert` |

## 1. Organização dos dados

- **Listas** guardam as séries históricas usadas na regressão (`historico_vento = [8, 10, 12]`,
  `historico_energia_eolica = [20, 25, 30]`) e a sequência de leituras dos ciclos.
- **Dicionários (chave-valor, ou seja, tabelas hash)** guardam cada leitura (`"solar"`, `"eolica"`,
  `"temp_interna"`…), o consumo por módulo (`{"oxigenio": 10, "agua": 6, …}`) e o estado dos
  equipamentos (`{"turbina_eolica_1": "OK"}`). O acesso por chave é O(1) em média.
- **Árvore** representa a hierarquia de sistemas. Dá para navegar por caminho
  (`buscar_por_caminho(colonia, ["Sistema energético", "Solar"])`). A partir dela, o sistema monta um
  índice `id → módulo` para consultas diretas.

```
Colônia Aurora Siger
└─ Sistema energético
  └─ Solar          (Painel solar A, Painel solar B)
  └─ Eólico         (Turbina eólica 1)
  └─ Baterias
└─ Suporte à vida   (oxigênio, água, controle térmico)       [essenciais]
└─ Comunicação      (antena Terra-Marte)                      [essencial]
└─ Produção         (estufa p4, laboratório p3, oficina p1)   [não essenciais]
└─ Habitação        (iluminação das áreas comuns p2)          [não essencial]
```

`pN` é a prioridade: quanto menor, mais cedo o módulo é desligado quando falta energia.

## 2. Regras de decisão

| # | Condição | Ação |
|---|---|---|
| 1 | Sempre | Suporte à vida e comunicação **ficam ligados** (nunca entram na lista de corte) |
| 2 | energia < 50 **e** consumo > 60 | `ALERTA: reduzir consumo` + **modo economia**: desliga todos os não essenciais |
| 3 | energia < 50 | `AVISO: energia baixa`: desliga não essenciais, da menor prioridade para a maior, até o consumo caber na geração |
| 4 | consumo > geração | Equilibra do mesmo jeito da regra 3 |
| 5 | Temperatura interna < 18 °C ou > 26 °C | Aumenta o aquecimento ou o resfriamento |
| 6 | Equipamento em `FALHA` | Alerta de manutenção (e a previsão deixa de contar com ele) |
| — | Nem os essenciais cabem na geração | `ALERTA CRÍTICO`: usar as baterias |

**Análise de energia:**
- consumo > geração gera `ALERTA: consumo maior que geração`;
- geração − consumo > 5 kW gera `SUGESTÃO: armazenar energia excedente`;
- diferença menor que isso significa equilíbrio.

## 3. Modelo de previsão

Regressão linear simples `y = a + b·x`, calculada à mão pelo método dos mínimos quadrados:

```
b = Σ(xi − x̄)(yi − ȳ) / Σ(xi − x̄)²        a = ȳ − b·x̄
```

| Modelo | Reta ajustada | R² |
|---|---|---|
| Eólico (vento em m/s → kW) | energia = 0 + 2,5 × vento | 1,000 |
| Solar (irradiância em W/m² → kW) | energia = 0 + 0,0505 × irradiância | 0,995 |

Exemplo do enunciado: vento = 11 m/s → energia ≈ **27,5 kW**.

Em cada ciclo, o sistema aplica os dois modelos à previsão do tempo para o ciclo seguinte. Se a
geração estimada for menor que o consumo, ele avisa já no ciclo atual, para carregar as baterias e
adiar tarefas.

## Exemplo de entrada e saída

Entrada (ciclo 2, tempestade de poeira, o mesmo caso do enunciado: energia = 40, consumo = 70):

```python
{"solar": 8, "eolica": 32, "temp_interna": 20,
 "consumo": {"oxigenio": 10, "agua": 6, "controle_termico": 10, "comunicacao": 4,
             "laboratorio": 14, "estufa": 10, "iluminacao": 6, "oficina": 10},
 "previsao_vento": 12, "previsao_irradiancia": 800}
```

Saída:

```
Ciclo 2: Tempestade de poeira
  Entrada: geração = 40 kW (solar 8 + eólica 32), consumo = 70 kW, temperatura interna = 20 °C
  -> PRIORIDADE: suporte à vida e comunicação LIGADOS (30 kW)
  -> ALERTA: reduzir consumo
  -> MODO ECONOMIA ativado: desligar todos os não essenciais
  -> DESLIGAR: Oficina de mineração (10 kW), Iluminação das áreas comuns (6 kW), Laboratório (14 kW), Estufa (10 kW)
  -> Consumo após a ação: 30 kW (antes: 70 kW)
  -> Análise do medido: ALERTA: consumo maior que geração (70 kW contra 40 kW)
  Previsão do tempo para o próximo ciclo: vento 12 m/s, irradiância 800 W/m² -> geração estimada 70.4 kW
  -> PREVISÃO: geração suficiente no próximo ciclo (sobra de 0.4 kW)
```

E o caso de sobra do enunciado (ciclo 3, geração = 80, consumo = 30):

```
  -> Análise do medido: SUGESTÃO: armazenar energia excedente (50 kW sobrando)
  -> PREVISÃO: déficit de 10.0 kW no próximo ciclo, carregar baterias agora e adiar tarefas não essenciais
```

A saída completa dos seis ciclos está em [`saida_exemplo.txt`](saida_exemplo.txt).

## Cenários simulados

| Ciclo | Situação | Geração × consumo | O que o sistema faz |
|---|---|---|---|
| 1 | Manhã estável | 55 × 52 | Equilíbrio; **prevê** o déficit da tempestade um ciclo antes |
| 2 | Tempestade de poeira | 40 × 70 | Modo economia: 70 → 30 kW |
| 3 | Pico de geração | 80 × 30 | Sugere armazenar 50 kW; prevê a noite sem sol |
| 4 | Noite fria | 20 × 45 | Corta não essenciais, aquece o habitat, usa as baterias para os essenciais |
| 5 | Falha na turbina | 38 × 48 | Corta oficina e laboratório, pede manutenção, previsão ignora a turbina |
| 6 | Tarde quente | 64 × 60 | Resfria o laboratório; prevê a queda de geração no fim da tarde |

## Relatório

O relatório em PDF está em [`relatorio/Relatorio_Fase3_Sistema_Colonia.pdf`](relatorio/Relatorio_Fase3_Sistema_Colonia.pdf).

## Autor

Luis Felipe Moraes Nicolau — FIAP, Ciência da Computação (1CCOS), 2026/2.
