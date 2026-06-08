# criação de um agente especialista em culinária com SLM
# Fase 3, Aula 3: Agente com cérebro de IA (SLM)

import os
import openai

class AgenteCulinarioSLM:
    def __init__(self):
        # configurar cliente da api do SLM
        # Ollama: base_url é a porta onde o Ollama está a rodar
        self.client = openai.OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        )
        self.modelo = "qwen2.5:3b" # nome do modelo no Ollama
        self.mensagens = [
            {
                "role": "system", 
                "content": (
                    "Você é o Agente Mestre Culinário, um chef de cozinha experiente e renomado. "
                    "Você NUNCA deve dizer que é o Claude, Anthropic, OpenAI ou ChatGPT. "
                    "Sua única identidade é ser um Chef Culinário prestativo. "
                    "Dê receitas incríveis baseadas nos ingredientes que o utilizador indicar. "
                    "Se o utilizador não fornecer ingredientes, pergunte o que ele quer cozinhar. "
                    "Seja criativo e dê instruções passo a passo."
                )
            },
        ]
    
    def percepcao(self):
        entrada = input("Você: ")
        return entrada
    
    def pensar(self, entrada):
        """envia a conversa toda ao SLM e devolve a resposta"""
        if entrada.lower() == "sair":
            return 'sair', None
        
        # Adiciona a mensagem do utilizador ao histórico
        self.mensagens.append({"role": "user", "content": entrada})

        try:
            resposta = self.client.chat.completions.create(
                model=self.modelo,
                messages=self.mensagens,
                temperature=0.2,
                max_tokens=500,
            )
            resposta_str = resposta.choices[0].message.content
            return 'resposta', resposta_str
        except Exception as e:
            print(f"Erro ao pensar: {e}")
            return 'erro', None
    
    def agir(self, acao, conteudo=None):
        if acao == 'sair':
            print("Agente encerrado. Até logo!")
            return False
        
        if acao == 'resposta':
            print(f"Agente mestre Culinário: {conteudo}")
            return True
        elif acao == 'erro':
            print(f"Erro: {conteudo}")
            return True
        
        return True
    
    def executar(self):
        print("Agente mestre Culinário iniciado. (Digite 'sair' para encerrar)\n")
        while True:
            entrada = self.percepcao()
            acao, conteudo = self.pensar(entrada)
            if not self.agir(acao, conteudo):
                break

if __name__ == "__main__":
    agente = AgenteCulinarioSLM()
    agente.executar()