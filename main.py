"""
Sistema inteligente da colônia Aurora Siger (FIAP, Fase 3).

Junta as três partes do projeto:
  dados.py      -> o que os sensores medem e como a colônia é organizada
  previsao.py   -> regressão linear simples (vento -> energia, sol -> energia)
  decisoes.py   -> regras automáticas e análise de energia

Execute com:  python3 main.py
"""

import dados
from estruturas import listar_arvore, buscar_por_caminho, construir_indice
from previsao import ajustar_reta, prever, coeficiente_r2, prever_geracao
from decisoes import consumo_total, decidir, analisar_energia, avaliar_previsao

LINHA = "=" * 72


def mostrar_organizacao():
    print(LINHA)
    print("1. ORGANIZAÇÃO DOS DADOS")
    print(LINHA)
    print("Hierarquia de sistemas (árvore):")
    for linha in listar_arvore(dados.colonia):
        print("  " + linha)

    solar = buscar_por_caminho(dados.colonia, ["Sistema energético", "Solar"])
    nomes = [f["nome"] for f in solar["filhos"]]
    print("\nNavegação: Sistema energético -> Solar ->", ", ".join(nomes))

    indice = construir_indice(dados.colonia)
    print(f"Índice chave-valor (tabela hash) com {len(indice)} itens.",
          f"Consulta direta indice['oxigenio'] -> {indice['oxigenio']['nome']}")


def treinar_modelos():
    print("\n" + LINHA)
    print("2. MODELO DE PREVISÃO (regressão linear simples)")
    print(LINHA)
    eolico = ajustar_reta(dados.historico_vento, dados.historico_energia_eolica)
    solar = ajustar_reta(dados.historico_irradiancia, dados.historico_energia_solar)
    r2_eolico = coeficiente_r2(eolico, dados.historico_vento, dados.historico_energia_eolica)
    r2_solar = coeficiente_r2(solar, dados.historico_irradiancia, dados.historico_energia_solar)

    print(f"Eólico: energia = {eolico['a']:.2f} + {eolico['b']:.2f} × vento      (R² = {r2_eolico:.3f})")
    print(f"Solar:  energia = {solar['a']:.2f} + {solar['b']:.4f} × irradiância (R² = {r2_solar:.3f})")
    print(f"Exemplo do enunciado: vento = 11 m/s -> energia ≈ {prever(eolico, 11):.1f} kW")
    return eolico, solar


def simular(eolico, solar):
    print("\n" + LINHA)
    print("3. SIMULAÇÃO DOS CICLOS (decisões e análise de energia)")
    print(LINHA)
    resumo = []
    for leitura in dados.leituras:
        geracao = leitura["solar"] + leitura["eolica"]
        consumo = consumo_total(leitura["consumo"])
        print(f"\nCiclo {leitura['ciclo']}: {leitura['descricao']}")
        print(f"  Entrada: geração = {geracao} kW (solar {leitura['solar']} + eólica {leitura['eolica']}),"
              f" consumo = {consumo} kW, temperatura interna = {leitura['temp_interna']} °C")
        for mensagem in decidir(leitura, dados.colonia):
            print("  -> " + mensagem)
        print("  -> Análise do medido: " + analisar_energia(geracao, consumo))

        prevista = prever_geracao(eolico, solar, leitura["previsao_vento"],
                                  leitura["previsao_irradiancia"], leitura["equipamentos"])
        print(f"  Previsão do tempo para o próximo ciclo: vento {leitura['previsao_vento']} m/s,"
              f" irradiância {leitura['previsao_irradiancia']} W/m²"
              f" -> geração estimada {prevista['total']:.1f} kW")
        print("  -> " + avaliar_previsao(prevista["total"], consumo))
        resumo.append((leitura["ciclo"], geracao, consumo, prevista["total"]))
    return resumo


def mostrar_resumo(resumo):
    print("\n" + LINHA)
    print("4. RESUMO: previsão feita em um ciclo x geração medida no ciclo seguinte")
    print(LINHA)
    print(f"  {'Ciclo':>5} | {'Geração':>8} | {'Consumo':>8} | {'Previsto p/ próximo':>20}")
    for ciclo, geracao, consumo, prevista in resumo:
        print(f"  {ciclo:>5} | {geracao:>8} | {consumo:>8} | {prevista:>20.1f}")
    for i in range(len(resumo) - 1):
        prevista = resumo[i][3]
        real = resumo[i + 1][1]
        print(f"  Ciclo {resumo[i][0]} previu {prevista:.1f} kW para o ciclo {resumo[i + 1][0]};"
              f" medido: {real} kW (erro de {abs(prevista - real):.1f} kW)")


def main():
    mostrar_organizacao()
    eolico, solar = treinar_modelos()
    resumo = simular(eolico, solar)
    mostrar_resumo(resumo)


if __name__ == "__main__":
    main()
