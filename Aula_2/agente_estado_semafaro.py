# Agente de ia com estado semafaro

#Transforme o semáforo que você fez no exercício da aula 1 num agente com memória. O agente deve:
# Ter um contador interno de quantos carros passaram desde a última vez que o sinal ficou verde para pedestres.
# Quando o utilizador escreve "carro":
# Se o contador de carros for menor que 3, o agente responde: "🟢 Sinal verde para carros. Pedestres esperam." e incrementa o contador.
# Se o contador atingir 3 ou mais, o agente automaticamente deve mudar para o modo pedestre: "🚶‍♂️ Prioridade para pedestres! Sinal vermelho para carros." e reinicia o contador para zero.
# Quando o utilizador escreve "pedestre", o agente responde imediatamente: "🚶‍♂️ Prioridade para pedestres! Sinal vermelho para carros." e também zera o contador de carros.
# O comando "emergencia" continua a funcionar: 🚨 "Todos param! Trânsito interrompido." (não mexe no contador).
# Qualquer outra entrada (exceto "sair") mostra: "Modo normal: sinal fechado para todos." e não altera o contador.
# "sair" encerra o agente.
# Dicas:
# Use uma classe com __init__ para guardar o contador.
# A lógica principal continua em pensar, que agora tem acesso a self.contador_carros.
# O agente deve agir de acordo com a entrada e com o estado atual do contador.
# Escreva o código, teste várias sequências (ex.: 3 carros seguidos, ou carro, pedestre, carro...) e veja se o comportamento está correto.

class AgenteSemaforoComMemoria:
    def __init__(self):
        #estado interno, memória do agente
        self.contador_carros = 0
    
    def percepcao(self):
        #continua lendo o input do utilizador
        entrada_str = input("Digite 'carro', 'pedestre' ou 'emergencia' ou 'sair': ")
        return entrada_str
    
    def pensar(self, entrada):
        if entrada.lower() == "sair":
            return 'sair'

        elif entrada.lower() == "carro":
            if self.contador_carros < 3:
                self.contador_carros += 1
                return 'verde_carros'
            else:
                self.contador_carros = 0
                return 'modo_pedestre'
        elif entrada.lower() == "pedestre":
            self.contador_carros = 0
            return 'modo_pedestre'
        elif entrada.lower() == "emergencia":
            return 'emergencia'
        else:
            return 'modo_normal'
        
    def agir(self, acao):
        if acao == 'sair':
            print("Agente encerrado. Até logo!")
            return False
        elif acao == 'modo_pedestre':
            print("🚶‍♂️ Prioridade para pedestres! Sinal vermelho para carros.")
            return True
        elif acao == 'emergencia':
            print("🚨 Todos param! Trânsito interrompido.")
            return True
        elif acao == 'modo_normal':
            print("Modo normal: sinal fechado para todos.")
            return True
        elif acao == 'verde_carros':
            print("🟢 Sinal verde para carros. Pedestres esperam.")
            return True
        else:
            return True

    def executar(self):
        print("Agente de semafaro com memória iniciado. (Digite 'sair' para encerrar )\n")
        while True:
            entrada = self.percepcao()
            acao = self.pensar(entrada)
            if not self.agir(acao):
                break

if __name__ == "__main__":
    agente = AgenteSemaforoComMemoria()
    agente.executar()