# FASE 5 - Aula 6: Arquiteturas avançadas - Planeamento e multi-agentes

Aqui o agente sabe conversar, usar ferramentas e até encadear várias ações. Mas ele ainda é reativo: decide o próximo passoà medida que executa. Agentes verdadeiramente sofisticadossão capazes de planear antes de agir, como um chefe que lê a receita inteira antes de pegar na faca. Além disso, podemos dividir o trabalho entre vários agentes especializados, é o conceito de multi-agentes.

## Nesta aula vamos construir:

1. Um agente planeador que recebe um objetivo complexo e o decompoe num plan textual (lista de passos).

2. Um agente executor que recebe o plano e executa cada passo, podendo usar ferramentas que já temos.

3. Uma orquestração simples que junta os dois: o **planeador** cria o plano, o **executor** segue-o.

No final, teremos um sistema capaz de resolver pedidos como "Organizar um jantar para 4 pessoas com entrada,prato principal e sobremesa. Dá-me a lista de compras com quantidades."

## o Agente planeador

O planeador é um agente que usa o mesmo modelo, mas com system prompt focado em decompor o problemas. Não executa ferramentas; apenas raciocinae escreve um plano.

Criamos uma classe **AgentePlaneador** que reaproveita a lógica de comunicação com SLM. Como o modelo é pequeno, vamos dar-lhe um prompt mais direto.
```python
    class AgentePlaneador:
        def __init__(self, client, modelo):
            self.client = client
            self.modelo = modelo
            self.mensagens = [
                {
                    "role": "system",
                    "content": (
                        "És um assistente especializado em planear tarefas. "
                        "Quando receberes um pedido, devolve APENAS um plano passo a passo, "
                        "numerado e claro. Não executes os passos, apenas descreve o que é preciso fazer. "
                        "Inclui detalhes como quantidades, tempos e ferramentas necessárias quando relevante."
                    )
                }
            ]

        def criar_plano(self, objetivo: str) -> str:
            self.mensagens.append({"role": "user", "content": objetivo})
            try:
                resp = self.client.chat.completions.create(
                    model=self.modelo,
                    messages=self.mensagens,
                    temperature=0.3,
                    max_tokens=500
                )
                plano = resp.choices[0].message.content
                self.mensagens.append({"role": "assistant", "content": plano})
                return plano
            except Exception as e:
                return f"Erro ao gerar plano: {e}"
```

## O agente executor (com ferramentas)

O executor é o nosso **AgenteFerramenta** já existente, mas agora recebe um plano e executa cada passo. Como o plano pode conter multiplos passos, vamos dar ao executor uma nova missão: ele recebe o plano como contexto inicial e segue as instruções.

Para simplificar, vamos reutilizar a classe **AgenteFerramenta** que já tem o ciclo ReAct, mas adicionamos um método **executar_plano** que inseri o plano como mensagem no sistema e depois pede ao utilizador (ou a um processo automático) que vá confirmando cada passo.Numa versão mais autonoma, poderiamos fazer o executor consumir o plano automáticamente, mas para manter o controle, faremos assim: o executor apresenta o próximo passoe pede confirmação (ou executa ferramentas se o passo exigir).

Mas para já, vamos fazer algo mais prático e visual: o executor lê o plano, identifica os passos que requerem a ferramentas (cálculos, conversões) e executa-os, mostrando o resultado. No final, deveolve o resumo.

Abordagem: Vamos manter o nosso AgenteFerramenta e adicionar o método **executar_plano(plano)** que inseri o plano no histórico e pede ao LLM ou SLM que execute os passos um a um, usando ferramentasquando necessário. O ciclo ReAct já trata disso.

```python
    class AgenteExecutor(AgenteFerramenta):
        def executar_plano(self, plano: str):
            """Recebe um plano e executa-o passo a passo, usando ferramentas se necessário."""
            print("\n📋 Plano recebido. A executar...\n")
            # Adiciona o plano como contexto do sistema
            self.mensagens.append({
                "role": "system",
                "content": f"Plano a seguir:\n{plano}\n\nSegue o plano passo a passo. Para cada passo que envolver cálculos ou conversões, usa as ferramentas disponíveis (calculadora, conversor). Quando terminares todos os passos, diz 'Plano concluído' e apresenta um resumo."
            })
            # Agora simulamos uma interação: o utilizador diz "Iniciar plano"
            self.mensagens.append({"role": "user", "content": "Iniciar plano."})

            # Chama o ciclo ReAct até terminar (máximo de iterações maior)
            MAX_ITERACOES = 10
            for _ in range(MAX_ITERACOES):
                resposta_str = self._chamar_slm()
                if resposta_str is None:
                    print("Erro na execução.")
                    return

                ferramenta, json_str = self._extrair_tool(resposta_str)
                if ferramenta:
                    self.mensagens[-1] = {"role": "assistant", "content": json_str}
                    resultado = self._executar_ferramenta(ferramenta)
                    self.mensagens.append({
                        "role": "user",
                        "content": f"Resultado da ferramenta ({ferramenta['tool']}): {resultado}"
                    })
                else:
                    # Se a resposta contiver "Plano concluído", terminamos
                    print(f"Agente Executor: {resposta_str}")
                    if "plano concluído" in resposta_str.lower():
                        print("\n✅ Execução finalizada.")
                        break
            else:
                print("Aviso: número máximo de iterações atingido.")
```

Repare que o executor herda de **AgenteFerramenta**, por isso tem acesso a todas as ferramentas  e ao ciclo ReAct.

## Orquestrador: juntar planeador e executor

Vamos criar um programa principal que:

1. Pergunta ao utilizador qual o objetivo.

2. Chama o **AgentePlaneador** para criar um plano.

3. Passa o plano ao **AgenteExecutor**, que o executa passo a passo.

```python
    def main():
        client = openai.OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )
        modelo = "qwen2.5:3b"

        print("🌟 Sistema Multi‑Agente de Culinária 🌟\n")

        objetivo = input("Qual é o seu pedido? (ex.: Jantar para 4 pessoas com entrada, prato principal e sobremesa)\n> ")

        # Fase 1: Planear
        print("\n⏳ A planear...")
        planeador = AgentePlaneador(client, modelo)
        plano = planeador.criar_plano(objetivo)
        print("\n📝 Plano gerado:\n")
        print(plano)
        print("\n" + "="*50)

        # Fase 2: Executar
        input("\nPressione Enter para executar o plano...")
        executor = AgenteExecutor()
        executor.client = client
        executor.modelo = modelo
        executor.mensagens = [executor.mensagens[0]]  # Mantém o system prompt original
        executor.executar_plano(plano)

    if __name__ == "__main__":
        main()
```

## Adaptação necessária: O system prompt do executor

O executor precisa saber que deve seguir o plano. O seu system prompt atual é o chef. Vamos torna-lo mais flexivel, recebendo o plano como parte do contexto. No método **executar_plano**, já estamos á adicionar uma mensagem de sistema extra. Mas atenção: o ```__init__``` original define um system prompt. Para não acumular lixo, ao inicializar o executor no main, podemos fazer.

```python
    executor = AgenteExecutor()
    executor.client = client
    executor.modelo = modelo
    # Substitui o system prompt pelo original (vamos guardá-lo e depois adicionar o plano)
    executor.system_prompt_base = executor.mensagens[0]["content"]
```

E dentro de **executor_plano**, recriamos as mensagens:

```python
    def executar_plano(self, plano):
        # Reinicia as mensagens com o system prompt base + plano
        self.mensagens = [
            {"role": "system", "content": self.system_prompt_base},
            {"role": "system", "content": f"Plano a seguir:\n{plano}\n\nSegue o plano..."}
        ]
        self.mensagens.append({"role": "user", "content": "Iniciar plano."})
        # ... resto do ciclo ReAct
```

## A parte do multiagente 2 

A parte do multi-agente 2 é a continuação do multi-agente 1 com mais um agente critico.

