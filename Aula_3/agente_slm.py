# agente de ia com SLM Local (Ollama)
# Fase 3, Aula 3: Agente com cérebro de IA (Ollama)
import os
import openai
from dotenv import load_dotenv

load_dotenv()

class AgenteConversadorLLM:
    def __init__(self):
        # Configurar cliente para apontar para o Ollama local
        # O Ollama roda por padrão na porta 11434
        self.client = openai.OpenAI(
            api_key="ollama", # O Ollama não exige chave real, mas o SDK pede preenchimento
            base_url="http://localhost:11434/v1", # URL padrão da API local do Ollama
        )
        
        # DEFINA AQUI O SEU MODELO QWEN
        # Certifique-se de que o nome está idêntico ao que aparece no comando 'ollama list'
        # Exemplos comuns: "qwen2.5", "qwen2.5:7b", "qwen2.5:1.5b", "qwen2.5-coder"
        self.modelo = "qwen2.5:3b" 
        
        self.mensagens = [
            {"role": "system", "content": "Você é um assistente prestativo e amigável."},
        ]
    
    def percepcao(self):
        entrada = input("Você: ")
        return entrada
    
    def pensar(self, entrada):
        """envia a conversa toda ao SLM local e devolve a resposta"""
        if entrada.lower() == "sair":
            return 'sair', None # Ajustado para retornar tupla e não quebrar o desempacotamento
        
        # Adiciona a mensagem do utilizador ao histórico
        self.mensagens.append({"role": "user", "content": entrada})

        try:
            resposta = self.client.chat.completions.create(
                model=self.modelo,
                messages=self.mensagens,
                temperature=0.7,
                max_tokens=500,
            )
            texto = resposta.choices[0].message.content
            # Adiciona a resposta ao histórico
            self.mensagens.append({"role": "assistant", "content": texto})
            return "responder", texto
        except Exception as e:
            print(f"Erro ao pensar: {e}")
            return "erro", None
        
    def agir(self, acao, conteudo=None):
        if acao == "sair":
            print("Agente encerrado. Até logo!")
            return False
        elif acao == "responder":
            print(f"Assistente: {conteudo}\n")
            return True
        elif acao == "erro":
            return True # continua o loop
        
        return True
    
    def executar(self):
        print(f"Agente conversador com SLM Local ({self.modelo}) iniciado.")
        print("(Digite 'sair' para encerrar )\n")
        while True:
            entrada = self.percepcao()
            acao, conteudo = self.pensar(entrada)
            if not self.agir(acao, conteudo):
                break

if __name__ == "__main__":
    # Como o Ollama é local, não precisamos travar o script pela falta da DEEPSEEK_API_KEY
    agente = AgenteConversadorLLM()
    agente.executar()