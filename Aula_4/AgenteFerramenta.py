# Aula 4: Agentes que usam ferramentas (Tool use)
# Fase 4, Aula 4: Agentes que usam ferramentas (Tool use)

import os
import openai

class AgenteFerramenta:
    def __init__(self):
        # configurar cliente da api do SLM ou LLM
        self.client = openai.OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        )
        self.modelo = "qwen2.5:3b"
        self.mensagens = [
            {
                "role": "system",
                "content": (
                    "Você é o Agente Mestre Culinário, um chef de cozinha experiente e renomado. "
                    "Você NUNCA deve dizer que é outro modelo. "
                    "Dê receitas incríveis baseadas nos ingredientes. "
                    "Se precisar fazer um cálculo matemático, responda EXATAMENTE neste formato (e mais nada):\n"
                    '{"tool": "calculadora", "expressao": "a expressao matematica"}\n'
                    "Após receber o resultado da calculadora, use-o para responder ao utilizador em linguagem natural."
                )
            },
        ]

    def percepcao(self):
        entrada = input("Você: ")
        return entrada
    
    def calcular(self,expressao: str) -> str:
        """Calcula uma expressão matemática simples (+, -, *, /, parênteses). Retorna string com resultado ou erro."""
        try:
            # Remove tudo que não seja número, operador, ponto, parênteses
            sanitizada = re.sub(r'[^0-9+\-*/().]', '', expressao)
            resultado = eval(sanitizada, {"__builtins__": None}, {})
            return f"{resultado}"
        except Exception as e:
            return f"Erro ao calcular: {e}"

    def _chamar_slm(self):
        try:
            resposta = self.client.chat.completions.create(
                model=self.modelo,
                messages=self.mensagens,
                temperature=0.2,
                max_tokens=500,
            )
            texto = resposta.choices[0].message.content
            self.mensagens.append({"role": "assistant", "content": texto})
            return texto
        except Exception as e:
            print(f"Erro ao chamar o SLM: {e}")
            return None

    def _extrair_tool(self, texto):
        """Tenta encontrar um JSON de tool. Retorna o dicionário ou None."""
        texto = texto.strip()
        if texto.startswith("{") and texto.endswith("}"):
            try:
                obj = json.loads(texto)
                if "tool" in obj and obj["tool"] == "calculadora" and "expressao" in obj:
                    return obj
            except json.JSONDecodeError:
                pass
        return None

    def _executar_ferramenta(self, tool_obj):
        expressao = tool_obj["expressao"]
        return calcular(expressao)

    def pensar(self, entrada):
        if entrada.lower() == "sair":
            return "sair", None
        
        # Adiciona a mensagem do utilizador ao histórico
        self.mensagens.append({"role": "user", "content": entrada})

        # primeira chamada ao SLM
        resposta_str = self._chamar_slm()
        if resposta_str is None:
            return "erro", "Falha ao chamar o SLM"

        # Tentar extrair um JSON de ferramenta
        possivel_ferramenta = self._extrair_tool(resposta_str)
        if possivel_ferramenta:
            # Executar a ferramenta e informar ao modelo
            resultado_ferramenta = self._executar_ferramenta(possivel_tool)
            self.mensagens.append({"role": "tool", "content": f"Resultado da calculadora: {resultado_ferramenta}"})
            
            # segunda chamada ao LLM ou SLM para gerar a resposta final
            reposta_final = self._chamar_slm()
            if reposta_final is None:
                return "erro", "Falha ao chamar o SLM"
            return "resposta", reposta_final
        else:
            # resposta normal
            return "resposta", resposta_str

    def agir(self, acao, conteudo=None):
        if acao == "sair":
            print("Agente mestre Culinário encerrado.")
            return False
        elif acao == "erro":
            print(f"Erro: {conteudo}")
            return True
        elif acao == "resposta":
            print(f"Agente mestre Culinário: {conteudo}")
            return True

    def executar(self):
        print("Agente mestre Culinário iniciado. (Digite 'sair' para encerrar)\n")
        while True:
            entrada = self.percepcao()
            acao, conteudo = self.pensar(entrada)
            if not self.agir(acao, conteudo):
                break

if __name__ == "__main__":
    agente = AgenteFerramenta()
    agente.executar()