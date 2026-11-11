"""
PREVISÃO: regressão linear simples feita à mão (método dos mínimos quadrados).

Modelo: y = a + b·x
    b = Σ (xi − x̄)(yi − ȳ) / Σ (xi − x̄)²
    a = ȳ − b·x̄

Não usa bibliotecas: só listas, laços e funções.
"""


def media(valores):
    """Média aritmética de uma lista."""
    soma = 0
    for v in valores:
        soma = soma + v
    return soma / len(valores)


def ajustar_reta(x, y):
    """
    Ajusta a reta y = a + b·x aos pontos (x, y).
    Devolve um dicionário {"a": intercepto, "b": inclinação}.
    """
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("as listas precisam ter o mesmo tamanho e pelo menos 2 pontos")
    x_medio = media(x)
    y_medio = media(y)
    numerador = 0
    denominador = 0
    for i in range(len(x)):
        numerador = numerador + (x[i] - x_medio) * (y[i] - y_medio)
        denominador = denominador + (x[i] - x_medio) ** 2
    if denominador == 0:
        raise ValueError("todos os valores de x são iguais: não há reta única")
    b = numerador / denominador
    a = y_medio - b * x_medio
    return {"a": a, "b": b}


def prever(modelo, x):
    """Aplica o modelo a um novo valor de x. Geração nunca fica negativa."""
    y = modelo["a"] + modelo["b"] * x
    if y < 0:
        return 0
    return y


def coeficiente_r2(modelo, x, y):
    """
    R² = 1 − SQres / SQtot: quanto da variação de y a reta explica
    (1 = explica tudo, 0 = não explica nada).
    """
    y_medio = media(y)
    sq_res = 0
    sq_tot = 0
    for i in range(len(x)):
        sq_res = sq_res + (y[i] - (modelo["a"] + modelo["b"] * x[i])) ** 2
        sq_tot = sq_tot + (y[i] - y_medio) ** 2
    if sq_tot == 0:
        return 1.0
    return 1 - sq_res / sq_tot


def prever_geracao(modelo_eolico, modelo_solar, vento, irradiancia, equipamentos):
    """
    Estima a geração total do próximo ciclo a partir da previsão do tempo.
    Um gerador em FALHA não entra na conta, mesmo com vento ou sol.
    """
    eolica = 0
    if equipamentos["turbina_eolica_1"] == "OK":
        eolica = prever(modelo_eolico, vento)
    solar = 0
    if equipamentos["painel_solar_A"] == "OK" or equipamentos["painel_solar_B"] == "OK":
        solar = prever(modelo_solar, irradiancia)
        if equipamentos["painel_solar_A"] != "OK" or equipamentos["painel_solar_B"] != "OK":
            solar = solar / 2  # só um dos dois painéis funcionando
    return {"eolica": eolica, "solar": solar, "total": eolica + solar}
