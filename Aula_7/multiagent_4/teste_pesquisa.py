from AgenteFerramenta_4 import AgenteFerramenta_4
import openai

agente = AgenteFerramenta_4()

# Chama o ciclo pensar (que agora inclui a possibilidade de pesquisa)
acao, conteudo = agente.pensar("Quanto custa 1kg de farinha de trigo convencional no Brasil hoje?")
print(conteudo)