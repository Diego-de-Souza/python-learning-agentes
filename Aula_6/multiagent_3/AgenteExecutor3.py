# agente executor 2
import re

from AgenteFerramenta_3 import AgenteFerramenta_3
import unicodedata

class AgenteExecutor3(AgenteFerramenta_3):
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

        # 1. Extrair passos numerados do plano (linhas que começam com número)
        passos = re.findall(r'(?:\d+[\.\)]\s?)(.*)', plano)
        if not passos:
            # Se não encontrar números, divide por linhas não vazias
            passos = [l.strip() for l in plano.splitlines() if l.strip()]
            # Se ainda não der, usa o plano inteiro como um passo único
            if not passos:
                passos = [plano]

        print(f"🔢 Foram identificados {len(passos)} passos no plano.\n")

        # 2. Percorrer cada passo, um a um
        resultados = []
        for i, passo in enumerate(passos):
            # Recria o histórico para cada passo, mantendo apenas o contexto essencial
            self.mensagens = [
                {"role": "system", "content": self.system_prompt_base},
                {"role": "system", "content": (
                    f"Estás a executar um plano. Já foram concluídos {i} de {len(passos)} passos.\n"
                    f"Próximo passo a executar:\n{passo}\n\n"
                    "Executa APENAS este passo. Usa ferramentas (calculadora, conversor) se necessário. "
                    "Responde de forma concisa com o que fizeste. Não peças confirmação."
                )}
            ]
            self.mensagens.append({"role": "user", "content": "Executa o passo acima."})

            # Ciclo interno para o passo atual (máximo 3 tentativas para ferramentas)
            concluido = False
            for tentativa in range(3):
                resposta_str = self._chamar_slm()
                if resposta_str is None:
                    resultados.append(f"Passo {i+1}: ERRO de comunicação.")
                    break

                ferramenta, json_str = self._extrair_tool(resposta_str)
                if ferramenta:
                    self.mensagens[-1] = {"role": "assistant", "content": json_str}
                    resultado_ferr = self._executar_ferramenta(ferramenta)
                    self.mensagens.append({
                        "role": "user",
                        "content": f"Resultado da ferramenta ({ferramenta['tool']}): {resultado_ferr}"
                    })
                    # Continua no ciclo interno para o modelo processar o resultado
                    continue
                else:
                    # Passo concluído sem necessidade de mais ferramentas
                    print(f"✅ Passo {i+1}/{len(passos)}: {resposta_str[:100]}...")
                    resultados.append(f"Passo {i+1}: {resposta_str}")
                    concluido = True
                    break

            if not concluido:
                resultados.append(f"Passo {i+1}: Falhou após 3 tentativas. Saltando.")
                print(f"⚠️ Passo {i+1} falhou. Saltando...")

        # 3. Gerar resumo final
        resumo = "\n".join(resultados)
        # Pede ao modelo um resumo global
        self.mensagens = [
            {"role": "system", "content": self.system_prompt_base},
            {"role": "system", "content": (
                f"Plano original:\n{plano}\n\n"
                f"Resultados da execução:\n{resumo}\n\n"
                "Faz um resumo final amigável do que foi realizado. Termina com 'Plano concluído.'."
            )}
        ]
        self.mensagens.append({"role": "user", "content": "Faz o resumo final."})
        resumo_final = self._chamar_slm()
        if resumo_final:
            print(f"\n📝 Resumo final:\n{resumo_final}")
            return resumo_final
        else:
            return "\n".join(resultados) + "\nPlano concluído."

