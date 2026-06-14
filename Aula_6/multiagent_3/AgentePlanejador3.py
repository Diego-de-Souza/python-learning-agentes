# AgentePlaneador 3

class AgentePlanejador3:
    def __init__(self, client, modelo):
        self.client = client
        self.modelo = modelo
        self.mensagens = [
            {
                "role": "system",
                "content": (
                    "Você é um especialista em planejar tarefas."
                    "Quando receber um pedido, vai devolver APENAS um plano passo a passo,"
                    "numerador e claro. Não execute os passos, apenas descreva o que é preciso fazer."
                    "Incluir detalhes como quantidades, tempos e ferramentas necessárias quando relevante."
                )
            }
        ]
    
    def criar_plano(self, objetivo: str) -> str:
        self.mensagens.append({
            "role": "user",
            "content": objetivo,
        })

        try:
            resp = self.client.chat.completions.create(
                model=self.modelo,
                messages=self.mensagens,
                temperature=0.3,
                max_tokens=800,
            )
            plano = resp.choices[0].message.content

            self.mensagens.append({
                "role": "assistant",
                "content": plano,
            })

            return plano
        except Exception as e:
            return f"Erro ao gerar plano: {e}"
            