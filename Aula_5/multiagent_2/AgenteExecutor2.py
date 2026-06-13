# agente executor 2

from AgenteFerramenta_2 import AgenteFerramenta_2
import unicodedata

class AgenteExecutor2(AgenteFerramenta_2):
    # verifica se o plano foi concluido
    def _plano_concluido(self, texto: str) -> bool:
        normalizado = unicodedata.normalize("NFD", texto.lower())
        normalizado = "".join(
            c for c in normalizado
            if unicodedata.category(c) != "Mn"
        )
        return "plano concluido" in normalizado

    def executar_plano(self, plano: str) -> str:
        """Recebe um plano e executa-o passo a passo, usando ferramentas se necessário."""
        print("\n Plano recebido. A executar...\n")

        # Adiciona o plano como contexto do sistema
        self.mensagens.append({
            "role": "system",
            "content": f"Plano a seguir:\n{plano}\n\nSegue o plano passo a passo. Para cada passo que envolver cálculos ou conversões, usa as ferramentas disponíveis (calculadora, conversor). Quando terminares todos os passos, diz 'Plano concluído' e apresenta um resumo."
        })

        # Agora simulamos uma interação: o utilizador diz "Iniciar plano"
        self.mensagens.append({
            "role": "user",
            "content": "Iniciar plano",
        })

        # Chama o ciclo ReAct até terminar (máximo de iterações maior)
        MAX_ITERACOES = 10
        for _ in range(MAX_ITERACOES):
            resposta_str = self._chamar_slm()
            if resposta_str is None:
                print("Erro na execução.")
                return
            
            if not resposta_str.strip():
                continue
            
            ferramenta, json_str = self._extrair_tool(resposta_str)
            if ferramenta:
                self.mensagens[-1] = {
                    "role": "assistant",
                    "content": json_str
                }
                resultado = self._executar_ferramenta(ferramenta)
                self.mensagens.append({
                    "role": "user",
                    "content": resultado,
                })
            if self._plano_concluido(resposta_str):
                print("\n Plano concluído. Resumo:\n")
                print(resposta_str)
                return resposta_str
        else:
            print("Aviso: número máximo de iterações atingido.")
            return "Plano não concluído devido a limitações técnicas."

