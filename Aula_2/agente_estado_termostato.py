# Agente de ia com estado termostato

class AgenteTermostatoComMemoria:
    def __init__(self):
        #estado interno, memória do agente
        self.aquecedor_ligado = False
        self.resfriador_ligado = False
    
    def percepcao(self):
        #continua lendo o input do utilizador
        temp_str = input("Temperatura atual do ambiente: (digite um numero ou sair) ")
        return temp_str
    
    def pensar(self, entrada):
        #agora a descisão usa o estado atual
        if entrada.lower() == "sair":
            return 'sair', None

        try:
            temperatura = float(entrada)
        except ValueError:
            print(" Entrada inválida, tente novamente.")
            return 'invalida', None
        
        #Histerese para o aquecedor
        if not self.aquecedor_ligado and temperatura < 18.0:
            self.aquecedor_ligado = True
            self.resfriador_ligado = False
            acao = 'ligar aquecedor'
        elif self.aquecedor_ligado and temperatura > 21.0:
            self.aquecedor_ligado = False
            acao = 'desligar aquecedor'
        #histerese para o resfriador
        elif not self.resfriador_ligado and temperatura > 26.0:
            self.resfriador_ligado = True
            self.aquecedor_ligado = False
            acao = 'ligar resfriador'
        elif self.resfriador_ligado and temperatura < 23.0:
            self.resfriador_ligado = False
            acao = 'desligar resfriador'
        else:
            acao = 'manter' #nada muda

        return acao, temperatura
    
    def agir(self, acao, temperatura=None):
        if acao == 'sair':
            print("Agente encerrado. Até logo!")
            return False
        elif acao == 'invalida':
            return True
        else:
            estado_geral = []
            if self.aquecedor_ligado:
                estado_geral.append("aquecedor ligado")
            if self.resfriador_ligado:
                estado_geral.append("resfriador ligado")
            if not estado_geral:
                estado_geral.append("Ambos desligados")

            print(f" Temperatura: {temperatura:.1f}°C -> Ação: {acao} -> Estado: {', '.join(estado_geral)}")
            return True
    
    def executar(self):
        print("Agente de termostato com memória iniciado. (Digite 'sair' para encerrar )\n")
        while True:
            entrada = self.percepcao()
            acao, temperatura = self.pensar(entrada)
            if not self.agir(acao, temperatura):
                break

if __name__ == "__main__":
    agente = AgenteTermostatoComMemoria()
    agente.executar()