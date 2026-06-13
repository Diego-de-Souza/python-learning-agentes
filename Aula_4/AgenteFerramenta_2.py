# Aula 4: Agentes que usam ferramentas (Tool use)
# Fase 4, Aula 4: Agentes que usam ferramentas (Tool use)

import os
import openai
import json
import re

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
                    "Se precisar converter unidades, responda EXATAMENTE neste formato (e mais nada):\n"
                    '{"tool": "conversor", "de": "unidade de origem", "para": "unidade de destino", "valor": "valor a converter"}\n'
                    "Após receber o resultado da calculadora ou conversor, use-o para responder ao utilizador em linguagem natural."
                )
            },
        ]
        # Sinónimos e fatores de conversão
        self.unidades_canonicas = {
            "g": "g", "gramas": "g", "grama": "g",
            "kg": "kg", "quilogramas": "kg", "quilos": "kg",
            "ml": "ml", "mililitros": "ml",
            "xicara": "xicara", "xicaras": "xicara", "xícara": "xicara",
            "colher de sopa": "colher_sopa", "colheres de sopa": "colher_sopa",
            "colher de cha": "colher_cha", "colheres de cha": "colher_cha",
            "copo": "copo", "copos": "copo",
            "lb": "lb", "libras": "lb",
            "oz": "oz", "onças": "oz",
        }
        self.fatores = {
            "g": {"xicara": 1/120, "colher_sopa": 1/15, "colher_cha": 1/5, "kg": 0.001, "oz": 0.035274},
            "kg": {"g": 1000, "lb": 2.20462, "oz": 35.274},
            "ml": {"xicara": 1/240, "colher_sopa": 1/15, "colher_cha": 1/5, "copo": 1/250},
            "xicara": {"ml": 240, "g": 120, "colher_sopa": 16, "colher_cha": 48},
            "colher_sopa": {"ml": 15, "colher_cha": 3},
            "colher_cha": {"ml": 5},
            "copo": {"ml": 250, "xicara": 1},
            "lb": {"g": 453.592, "kg": 0.453592, "oz": 16},
            "oz": {"g": 28.3495, "lb": 0.0625},
        }

    def percepcao(self):
        entrada = input("Você: ")
        return entrada
    
    def calcular(self, expressao: str) -> str:
        """Calcula uma expressão matemática simples (+, -, *, /, parênteses). Retorna string com resultado ou erro."""
        try:
            # Remove tudo que não seja número, operador, ponto, parênteses
            sanitizada = re.sub(r'[^0-9+\-*/().]', '', expressao)
            resultado = eval(sanitizada, {"__builtins__": None}, {})
            return f"{resultado}"
        except Exception as e:
            return f"Erro ao calcular: {e}"

    def converter(self, de: str, para: str, valor: float) -> str:
        """Converte um valor de uma unidade para outra. Retorna string com resultado ou erro."""
        try:
            de = self.unidades_canonicas.get(de.lower().strip())
            para = self.unidades_canonicas.get(para.lower().strip())

            if not de or not para:
                return f"Erro: unidade desconhecida ('{de}' ou '{para}')"
            
            if de == para:
                return f'{valor} {de} são {valor} {para} (mesma unidade)'
            
            if para not in self.fatores[de]:
                return f"Erro: conversão de {de} para {para} não suportada"
            
            fator = self.fatores[de][para]
            resultado = valor * fator
            return f"{valor} {de} são {resultado:.2f} {para}"
        except Exception as e:
            return f"Erro ao converter: {e}"

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
        """Tenta extrair o primeiro objeto JSON de tool, mesmo que haja texto extra."""
        texto = texto.strip()

        # Remove blocos markdown
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0].strip()

        # Usa raw_decode para pegar apenas o primeiro objeto JSON
        try:
            decoder = json.JSONDecoder()
            obj, idx = decoder.raw_decode(texto)
            if isinstance(obj, dict) and "tool" in obj:
                if obj["tool"] in ["calculadora", "conversor"]:
                    # Retorna também a string JSON exata que foi decodificada
                    json_str = texto[:idx]
                    return obj, json_str
        except json.JSONDecodeError:
            pass

        return None, None

    def _executar_ferramenta(self, tool_obj):
        if tool_obj["tool"] == "calculadora":
            expressao = tool_obj["expressao"]
            return self.calcular(expressao)
        elif tool_obj["tool"] == "conversor":
            de = tool_obj["de"]
            para = tool_obj["para"]
            valor = tool_obj["valor"]
            return self.converter(de, para, valor)
        return None

    def pensar(self, entrada):
        if entrada.lower() == "sair":
            return "sair", None

        self.mensagens.append({"role": "user", "content": entrada})

        MAX_ITERACOES = 5
        for _ in range(MAX_ITERACOES):
            resposta_str = self._chamar_slm()
            if resposta_str is None:
                return "erro", "Falha na comunicação com o modelo."

            ferramenta, json_extraido = self._extrair_tool(resposta_str)

            if ferramenta:
                # Substitui a última mensagem do assistente pelo JSON limpo
                # (remove a "sujidade" da resposta que continha texto extra)
                self.mensagens[-1] = {"role": "assistant", "content": json_extraido}

                # Executa a ferramenta e informa o modelo
                resultado = self._executar_ferramenta(ferramenta)
                self.mensagens.append({
                    "role": "user",
                    "content": f"Resultado da ferramenta ({ferramenta['tool']}): {resultado}"
                })
            else:
                # Resposta final sem ferramenta
                return "resposta", resposta_str

        # Excedeu iterações, devolve a última resposta
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