# FASE 4 - Aula 4: Agentes que usam ferramentas (Tool use)

Até agora o agente conversa, mas está "cego" e "preso" dentro da sua própria mente. Para se tornar verdadeiramente util, o agente de IA precisa agir no mundo real: fazer calculos, pesquisar na internet, consultar uma base de dados, enviar emails, etc. Essas opções são ferramentas (tools) que o agente pode invocar.

Nesta aula vamos dar ao nosso agente culinário uma ferramentamuito simples: uma calculadora. Assim, quando o utilizador perguntar "Quantas gramas são 3/4 de 200g?" ou "se eu dobrar a receita, quanto de farinha preciso?", o agente pode pedir ajuda a calculadora ao invés de inventar um numero.

Para facilitar estamos usando o Qwen2.5 em modo local e não a api do Openai, então não temos o suporte nativo a função calling, vamos mostrar uma técnica poderosa que funciona com qualquer modelo: o agente "fala" um formato especial (JSON) e o nosso código interpreta isso como um pedido de ferramenta. Este é o mesmo principio que o function calling faz por trás, só que nós controlamos tudo.

## O ciclo mental com ferramentas

1. O agente recebe a pergunta do utilizador.

2. O LLM ou SLM decide se precisa de uma ferramenta. Se sim, responde com um JSON especial.

3. O nosso código deteta esse JSON, executa a ferramenta e devolve o resultado ao LLM ou SLM.

4. O LLM ou SLM recebe o resultado e gera a resposta final para o utilizador.

```text
    Usuário: "Quanto é 3/4 de 200g?"
    ↓
    LLM ou SLM: {"tool": "calculadora", "expressao": "3/4 * 200"}
    ↓
    Código Python: executa eval("3/4 * 200") → 150.0
    ↓
    LLM ou SLM recebe: "Resultado da calculadora: 150.0"
    ↓
    LLM ou SLM: "3/4 de 200g são 150g. Na receita, use 150g."
```

usaremos o novo ficheiro agente_ferramenta.py

## Implementação passo a passo
Vamos modificar o seu AgenteCulinarioSLM para incluir a ferramenta calculadora. Criaremos um novo ficheiro, agente_ferramentas.py.

1. Adicionar a ferramenta como uma função Python
Vamos fazer algo seguro, sem usar eval diretamente com expressões arbitrárias. Usaremos um parser simples que aceita operações matemáticas básicas.
```python
    import re

    def calcular(expressao: str) -> str:
        """Calcula uma expressão matemática simples (+, -, *, /, parênteses). Retorna string com resultado ou erro."""
        try:
            # Remove tudo que não seja número, operador, ponto, parênteses
            sanitizada = re.sub(r'[^0-9+\-*/().]', '', expressao)
            resultado = eval(sanitizada, {"__builtins__": None}, {})
            return f"{resultado}"
        except Exception as e:
            return f"Erro ao calcular: {e}"
```
Nota: eval com restrições é seguro aqui porque só permitimos números e operadores. Mas sinta‑se à vontade para usar um parser mais robusto se preferir.

2. Modificar o system prompt
Vamos instruir o modelo a responder com um JSON específico apenas quando precisar da calculadora.
```python
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
```

3. No método pensar, detetar e tratar o pedido de ferramenta
A ideia: quando o LLM ou SLM devolve uma resposta, tentamos interpretá‑la como JSON. Se contiver "tool": "calculadora", executamos a ferramenta e voltamos a chamar o modelo com o resultado.

```python
    import json

    def pensar(self, entrada):
        if entrada.lower() == "sair":
            return "sair", None

        self.mensagens.append({"role": "user", "content": entrada})

        # Primeira chamada ao LLM
        resposta_str = self._chamar_llm()
        if resposta_str is None:
            return "erro", "Falha na comunicação com o LLM"

        # Tentar extrair um JSON de ferramenta
        possivel_tool = self._extrair_tool(resposta_str)
        if possivel_tool:
            # Executar a ferramenta e informar o modelo
            resultado_ferramenta = self._executar_ferramenta(possivel_tool)
            self.mensagens.append({"role": "user", "content": f"Resultado da calculadora: {resultado_ferramenta}"})
            # Segunda chamada ao LLM ou SLMpara gerar a resposta final
            resposta_final = self._chamar_llm()
            if resposta_final is None:
                return "erro", "Falha após ferramenta"
            return "resposta", resposta_final
        else:
            # Resposta normal
            return "resposta", resposta_str
```

4. Métodos auxiliares:
```python
    def _chamar_llm(self):
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
            print(f"Erro ao comunicar com o LLM: {e}")
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
```

5. Ajustar agir
Não precisa de grandes mudanças. Quando acao == "resposta", imprime o conteúdo.

6. Código completo
Junte tudo na classe AgenteCulinarioComFerramentas. Vou deixá‑lo escrever a versão final, mas aqui fica a estrutura pronta para copiar.

### Comando de teste

Você pode utilizar alguns comandos para testar, os comandos:

+ “Quanto é 200 * 0.75?”

+ “Numa receita que leva 500g de farinha para 4 pessoas, quanta farinha para 6?”

+ “Se eu tenho 3 ovos e a receita pede 4, qual a percentagem que falta?”

O agente deve detetar que precisa de calcular, pedir a ferramenta e dar a resposta final.


