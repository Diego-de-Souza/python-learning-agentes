from AgenteFerramenta_5 import AgenteFerramenta_5
import openai

agente = AgenteFerramenta_5()

# Chama o ciclo pensar (que agora inclui a possibilidade de pesquisa)
acao, conteudo = agente.pensar("O que é brunoise?")
print(conteudo)