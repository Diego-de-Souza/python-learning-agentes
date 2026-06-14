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

    # AgenteExecutor.py (novo executar_plano autónomo)
    def executar_plano(self, plano: str) -> str:
        print("\n📋 Plano recebido. A executar automaticamente...\n")

        # Limpa o histórico e recria com as instruções corretas
        self.mensagens = [
            {"role": "system", "content": self.system_prompt_base},
            {"role": "system", "content": (
                f"Plano a seguir:\n{plano}\n\n"
                "Segue o plano passo a passo, um passo por cada resposta. "
                "Para cada passo que envolver cálculos ou conversões, usa as ferramentas disponíveis "
                "(calculadora, conversor). Não peças confirmação ao utilizador. "
                "Apenas executa e descreve o que fizeste. "
                "Quando TODOS os passos estiverem concluídos, termina com 'Plano concluído.' e faz um resumo."
            )}
        ]
        # Arranque automático
        self.mensagens.append({"role": "user", "content": "Começa a executar o plano."})

        MAX_ITERACOES = 15
        for i in range(MAX_ITERACOES):
            resposta_str = self._chamar_slm()
            if resposta_str is None:
                print("❌ Erro de comunicação com o modelo.")
                return "Erro de comunicação."

            ferramenta, json_str = self._extrair_tool(resposta_str)

            if ferramenta:
                # Substitui a última mensagem (assistant) pelo JSON limpo
                self.mensagens[-1] = {"role": "assistant", "content": json_str}
                resultado = self._executar_ferramenta(ferramenta)
                self.mensagens.append({
                    "role": "user",
                    "content": f"Resultado da ferramenta ({ferramenta['tool']}): {resultado}"
                })
            else:
                # Mostra um extrato do passo executado
                print(f"🟢 Passo {i+1}: {resposta_str[:120]}...")

                # Verifica se o plano terminou
                if "plano concluído" in resposta_str.lower() or "execução finalizada" in resposta_str.lower():
                    print("\n✅ Plano concluído automaticamente.\n")
                    return resposta_str

                # Caso contrário, pede o próximo passo automaticamente
                self.mensagens.append({"role": "user", "content": "Próximo passo, por favor."})

        print("⚠️ Aviso: número máximo de iterações atingido.")
        return "Plano não concluído (limite de passos atingido)."

