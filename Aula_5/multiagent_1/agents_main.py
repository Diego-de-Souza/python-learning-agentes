# agents_main.py

import os
import openai
from AgentePlaneador import AgentePlaneador
from AgenteExecutor import AgenteExecutor

def main():
    client = openai.OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1",
    )
    modelo = "qwen2.5:3b"

    print("Sistema Multi-agentes de culinária \n")

    objetivo = input("Qual é o seu pedido? (ex.: Jantar para 4 pessoas com entrada, prato principal e sobremesa)\n")

    # Fase 1: Planear
    print("\nA Planear...")
    planeador = AgentePlaneador(client, modelo)
    plano = planeador.criar_plano(objetivo)
    print("\n Plano gerado:\n")
    print(plano)
    print("\n" + "="*50)

    # Fase 2: Executar
    input("\nPressione Enter para executar o plano...")
    executor = AgenteExecutor()
    executor.client = client
    executor.modelo = modelo
    executor.mensagens = [executor.mensagens[0]] # Mantem o system prompt original
    executor.executar_plano(plano)
    

if __name__ == "__main__":
    main()
    
