# a parte do multi-agente 2 é a continuação do multi-agente 1 com mais um agente critico.
# AgenteMain

import os
import openai
from AgentePlanejador3 import AgentePlanejador3
from AgenteExecutor3 import AgenteExecutor3
from AgenteCritico2 import AgenteCritico2

def Main3():
    client = openai.OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1",
    )
    modelo = "qwen2.5:3b"

    print("Sistema Multi-agentes de culinária \n")

    objetivo = input("Qual é o seu pedido? (ex.: Jantar para 4 pessoas com entrada, prato principal e sobremesa)\n")

    # Fase 1: Planear
    print("\nA Planear...")
    planeador = AgentePlanejador3(client, modelo)
    plano = planeador.criar_plano(objetivo)
    print("\n Plano gerado:\n")
    print(plano)
    print("\n" + "="*50)
    
    # Fase 2: Executar
    executor = AgenteExecutor3()
    executor.client = client
    executor.modelo = modelo
    executor.system_prompt_base = executor.mensagens[0]["content"]
    executor.mensagens = [executor.mensagens[0]] # Mantem o system prompt original
    resultado_execucao = executor.executar_plano(plano)
    print("\n Resumo da execução:\n")
    print(resultado_execucao)

    # Fase 3: Criticar
    critico = AgenteCritico2(client, modelo)
    critica = critico.criticar(plano, resultado_execucao)
    print("\n Crítica:\n")
    print(critica)
    print("\n" + "="*50)

if __name__ == "__main__":
    Main3()
    