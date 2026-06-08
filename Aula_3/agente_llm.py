# agente de ia com llm
# Fase 3, Aula 3: Agente com cérebro de IA (LLM)
import os
import openai
from dotenv import load_dotenv

load_dotenv()

class AgenteConversadorLLM:
    def __init__(self):
        # configurar cliente da api do LLM
        # DeepSeek: base_url própria, mas usamos a interface padrão do OpenAI
        self.client = openai.OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self.modelo = "deepseek-chat" # nome do modelo no DeepSeek  (ou gpt-3.5-turbo para OpenAI)
        self.mensagens = [
            {"role": "system", "content": "Você é um assistente prestativo e amigável."},
        ]
    
    def percepcao(self):
        entrada = input("Você: ")
        return entrada
    
    def pensar(self, entrada):
        """envia a conversa toda ao LLM e devolve a resposta"""
        if entrada.lower() == "sair":
            return 'sair', None
        
        # Adiciona a mensagem do utilizador ao histórico
        self.mensagens.append({"role": "user", "content": entrada})

        try:
            resposta =  self.client.chat.completions.create(
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
            print(f"Assistente: {conteudo}")
            return True
        elif acao == "erro":
            return True #continua o loop
        
        return True
    
    def executar(self):
        print("Agente conversador com LLM iniciado. (Digite 'sair' para encerrar )\n")
        while True:
            entrada = self.percepcao()
            acao, conteudo = self.pensar(entrada)
            if not self.agir(acao, conteudo):
                break

if __name__ == "__main__":
    # Verifica se a chave da api está definida
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("Erro: Chave da API não definida. Verifique o arquivo .env")
        print("defina a chave antes de executar o agente")
        exit(1)
    
    agente = AgenteConversadorLLM()
    agente.executar()