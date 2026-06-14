# AgenteCritico 2

class AgenteCritico:
    def __init__(self, client, modelo):
        self.client = client
        self.modelo = modelo
        self.mensagens = [
            {
                "role": "system",
                "content": (
                    "És um crítico culinário experiente. Vais receber um plano e o resumo da sua execução. "
                    "Analisa a qualidade do plano e da execução: o que foi bem feito, o que falta, "
                    "sugestões de melhoria, ajustes nas quantidades, tempos, etc. "
                    "Sê construtivo e específico."
                )
            }
        ]
    
    def criticar(self, plano: str, resultado_execucao: str) -> str:
        entrada = f"Plano original:\n{plano}\n\nResumo da execução:\n{resultado_execucao}"
        self.mensagens.append({"role": "user", "content": entrada})
        try:
            resp = self.client.chat.completions.create(
                model=self.modelo,
                messages=self.mensagens,
                temperature=0.4,
                max_tokens=500
            )
            critica = resp.choices[0].message.content
            self.mensagens.append({"role": "assistant", "content": critica})
            return critica
        except Exception as e:
            return f"Erro ao gerar crítica: {e}"