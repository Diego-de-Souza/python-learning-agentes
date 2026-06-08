## Agente de ia reativo semafaro sem memória

## Quero que modifique o agente para que ele funcione como um semáforo simples (luzes de trânsito), mas que recebe do ambiente um comando do utilizador:
## Se o utilizador escrever "carro", o agente deve imprimir 🚦 "Abrir sinal verde".
## Se escrever "pedestre", deve imprimir 🚶 "Fechar sinal para carros, abrir para pedestres".
## Se escrever "emergencia", deve imprimir 🚨 "Todos param!".
## Qualquer outra coisa: "Modo normal: sinal fechado".
## "sair" encerra o agente.

def percepcao():
    """Lê a entrada do utilizador (simula via input do utilizador)"""
    entrada = input("Digite 'carro', 'pedestre' ou 'emergencia' ou 'sair': ")
    return entrada

def pensar(entrada):
    """Decide a ação com base na leitura.
    Retorna: ação (string)."""

    if entrada.lower() == "sair":
        return 'sair'

    if entrada.lower() == "carro":
        return "Abrir sinal verde"
    elif entrada.lower() == "pedestre":
        return "Fechar sinal para carros, abrir para pedestres"
    elif entrada.lower() == "emergencia":
        return "Todos param!"
    else:
        return "Modo normal: sinal fechado"

def agir(acao):
    """Executa a ação decidida."""
    if acao == 'sair':
        print("Agente encerrado. Até logo!")
        return False
    else:
        print(f"Ação: {acao}")
        return True
    

def executar_agente():
    print("Agente de semafaro iniciado. (Digite 'sair' para encerrar )\n")
    while True:
        entrada = percepcao()
        acao = pensar(entrada)
        continuar = agir(acao)
        if not continuar:
            break

if __name__ == "__main__":
    executar_agente()