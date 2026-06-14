# Aula 7: Base do agente com ferramentas (reutilizado da Aula 4)

import openai
import json
import re
from ddgs import DDGS


class AgenteFerramenta_6:
    def __init__(self):
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
                    "\nPara perguntas sobre preços atuais, notícias, eventos recentes ou informações de hoje, "
                    "você DEVE usar a ferramenta pesquisar. responda EXATAMENTE neste formato (e mais nada):\n"
                    '{"tool": "pesquisar", "consulta": "a sua pergunta"}\n'
                    "Se precisar de um termo culinário, responda EXATAMENTE neste formato (e mais nada):\n"
                    '{"tool": "dicionario", "termo": "o termo culinário"}\n'
                    "Se precisar de uma receita da sua base de dados pessoal, responda EXATAMENTE neste formato:\n"
                    '{"tool": "receita", "nome": "nome da receita"}\n'
                )
            },
        ]
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
        with open("dicionario.json", "r", encoding="utf-8") as f:
            self.dicionario = json.load(f)
        with open("receitas.json", "r", encoding="utf-8") as f:
            self.receitas = json.load(f)

    def percepcao(self):
        entrada = input("Você: ")
        return entrada

    def calcular(self, expressao: str) -> str:
        """Calcula uma expressão matemática simples (+, -, *, /, parênteses)."""
        try:
            sanitizada = re.sub(r'[^0-9+\-*/().]', '', expressao)
            resultado = eval(sanitizada, {"__builtins__": None}, {})
            return f"{resultado}"
        except Exception as e:
            return f"Erro ao calcular: {e}"

    def converter(self, de: str, para: str, valor) -> str:
        """Converte um valor de uma unidade para outra."""
        try:
            valor = float(valor)
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
        """Extrai o primeiro objeto JSON de tool. Retorna (obj, json_str) ou (None, None)."""
        texto = texto.strip()

        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].split("```")[0].strip()

        try:
            decoder = json.JSONDecoder()
            obj, idx = decoder.raw_decode(texto)
            if isinstance(obj, dict) and "tool" in obj:
                if obj["tool"] in ["calculadora", "conversor", "pesquisar", "dicionario", "receita"]:
                    json_str = texto[:idx]
                    return obj, json_str
        except json.JSONDecodeError:
            pass

        return None, None

    def _executar_ferramenta(self, tool_obj):
        if tool_obj["tool"] == "calculadora":
            return self.calcular(tool_obj["expressao"])
        elif tool_obj["tool"] == "conversor":
            return self.converter(tool_obj["de"], tool_obj["para"], tool_obj["valor"])
        elif tool_obj["tool"] == "pesquisar":
            return self.pesquisar_web(tool_obj["consulta"])
        elif tool_obj["tool"] == "dicionario":
            return self.definir_termo(tool_obj["termo"])
        elif tool_obj["tool"] == "receita":
            return self.consultar_receita(tool_obj["nome"])
        return None

    def pensar(self, entrada):
        if entrada.lower() == "sair":
            return "sair", None

        self.mensagens.append({"role": "user", "content": entrada})

        MAX_ITERACOES = 5
        for _ in range(MAX_ITERACOES):
            print(f'ITERACAO {_ + 1} de {MAX_ITERACOES}')
            print(f'Chamando o SLM... (Mensagens: {len(self.mensagens)})')
            print(f'Mensagens: {self.mensagens}')


            resposta_str = self._chamar_slm()

            print(f'Resposta: {resposta_str}')
            
            if resposta_str is None:
                return "erro", "Falha na comunicação com o modelo."

            ferramenta, json_extraido = self._extrair_tool(resposta_str)

            if ferramenta:
                self.mensagens[-1] = {"role": "assistant", "content": json_extraido}
                resultado = self._executar_ferramenta(ferramenta)
                self.mensagens.append({
                    "role": "user",
                    "content": f"Resultado da ferramenta ({ferramenta['tool']}): {resultado}"
                })
            else:
                return "resposta", resposta_str

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

    def pesquisar_web(self, consulta: str, max_resultados: int = 3) -> str:
        """
        Pesquisa na web usando DuckDuckGo (via ddgs) e devolve um resumo.
        """
        try:
            with DDGS() as ddgs:
                # O método text() retorna um gerador, convertemos em lista para iterar sobre os resultados
                resultados = list(ddgs.text(consulta, max_results=max_resultados))
                print("RESULTADOS:")
                print(resultados)
            
                if not resultados:
                    return "Nenhum resultado encontrado para esta pesquisa."
                
                linhas = []
                for i, r in enumerate(resultados, 1):
                    titulo = r.get('title', 'Sem título')
                    corpo = r.get('body', '')
                    # Limita o tamanho do corpo para não encher o histórico
                    if corpo:
                        corpo_resumido = corpo[:200] + "..." if len(corpo) > 200 else corpo
                    else:
                        corpo_resumido = "(sem descrição)"
                    linhas.append(f"{i}. {titulo}\n   {corpo_resumido}")
                
                return "\n\n".join(linhas)
        except Exception as e:
            return f"Erro ao pesquisar na web: {e}"
    
    # Definir um termo culinário
    def definir_termo(self, termo: str) -> str:
        termo = termo.lower().strip()
        return self.dicionario.get(termo, f"O termo '{termo}' não está no meu dicionário.")
    
    # Consultar uma receita
    def consultar_receita(self, nome: str) -> str:
        """Procura uma receita pelo nome no ficheiro receitas.json e devolve os dados."""
        try:
            # Percorre as receitas e verifica se o nome contém a palavra pesquisada
            for receita in self.receitas:
                if nome.lower() in receita["nome"].lower():
                    texto = f"Receita: {receita['nome']}\n"
                    texto += f"Porções: {receita['porcoes']}\n"
                    texto += "Ingredientes:\n"
                    for ingrediente, quantidade in receita["ingredientes"].items():
                        texto += f"  - {ingrediente}: {quantidade}\n"
                    texto += "Passos:\n"
                    for i, passo in enumerate(receita["passos"], 1):
                        texto += f"  {i}. {passo}\n"
                    return texto.strip()
            return f"Nenhuma receita encontrada com o nome '{nome}'."
        except FileNotFoundError:
            return "Erro: ficheiro receitas.json não encontrado."
        except json.JSONDecodeError:
            return "Erro: ficheiro receitas.json está mal formatado."
        except Exception as e:
            return f"Erro ao consultar receita: {e}"

    def executar(self):
        print("Agente mestre Culinário iniciado. (Digite 'sair' para encerrar)\n")
        while True:
            entrada = self.percepcao()
            acao, conteudo = self.pensar(entrada)
            if not self.agir(acao, conteudo):
                break
    

if __name__ == "__main__":
    agente = AgenteFerramenta_4()
    agente.executar()
