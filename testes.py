"""
Testes simples, sem bibliotecas. Execute com:  python3 testes.py
Cada teste confere um exemplo pedido no enunciado.
"""

import dados
from estruturas import buscar_por_caminho, construir_indice, consumidores_nao_essenciais
from previsao import ajustar_reta, prever
from decisoes import decidir, analisar_energia


def leitura(solar, eolica, consumo, temp=22, turbina="OK"):
    return {
        "solar": solar, "eolica": eolica, "temp_interna": temp, "consumo": consumo,
        "equipamentos": {"painel_solar_A": "OK", "painel_solar_B": "OK",
                         "turbina_eolica_1": turbina, "baterias": "OK"},
    }


def testar_estruturas():
    assert buscar_por_caminho(dados.colonia, ["Sistema energético", "Eólico"])["nome"] == "Eólico"
    assert buscar_por_caminho(dados.colonia, ["Não existe"]) is None
    assert construir_indice(dados.colonia)["agua"]["essencial"] is True
    ordem = [m["id"] for m in consumidores_nao_essenciais(dados.colonia)]
    assert ordem == ["oficina", "iluminacao", "laboratorio", "estufa"]


def testar_regressao():
    modelo = ajustar_reta([8, 10, 12], [20, 25, 30])
    assert abs(modelo["b"] - 2.5) < 1e-9 and abs(modelo["a"]) < 1e-9
    assert abs(prever(modelo, 11) - 27.5) < 1e-9   # enunciado: vento 11 -> ≈ 27


def testar_decisoes():
    # Enunciado: energia = 40, consumo = 70 -> "ALERTA: reduzir consumo"
    consumo = {"oxigenio": 10, "agua": 6, "controle_termico": 10, "comunicacao": 4,
               "laboratorio": 14, "estufa": 10, "iluminacao": 6, "oficina": 10}
    mensagens = decidir(leitura(8, 32, consumo), dados.colonia)
    assert "ALERTA: reduzir consumo" in mensagens
    assert any("MODO ECONOMIA" in m for m in mensagens)
    assert "Consumo após a ação: 30 kW (antes: 70 kW)" in mensagens

    # Essenciais nunca são desligados, mesmo sem energia
    mensagens = decidir(leitura(0, 5, {"oxigenio": 10, "agua": 6, "estufa": 8}), dados.colonia)
    desligar = [m for m in mensagens if m.startswith("DESLIGAR")][0]
    assert "Estufa" in desligar and "oxigênio" not in desligar
    assert any("ALERTA CRÍTICO" in m for m in mensagens)

    # Energia sobrando: nenhuma ação de corte
    mensagens = decidir(leitura(45, 35, {"oxigenio": 10, "estufa": 4}), dados.colonia)
    assert not any(m.startswith("DESLIGAR") or m.startswith("ALERTA") for m in mensagens)

    # Temperatura e falha de equipamento
    mensagens = decidir(leitura(40, 0, {"oxigenio": 10}, temp=16, turbina="FALHA"), dados.colonia)
    assert any("aumentar aquecimento" in m for m in mensagens)
    assert any("turbina_eolica_1 em FALHA" in m for m in mensagens)


def testar_analise_energia():
    assert analisar_energia(40, 70).startswith("ALERTA: consumo maior que geração")
    assert analisar_energia(80, 30).startswith("SUGESTÃO: armazenar energia excedente")
    assert analisar_energia(55, 52).startswith("OK")


if __name__ == "__main__":
    testar_estruturas()
    testar_regressao()
    testar_decisoes()
    testar_analise_energia()
    print("Todos os testes passaram.")
