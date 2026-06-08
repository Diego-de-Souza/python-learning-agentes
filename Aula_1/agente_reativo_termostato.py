## Agente de ia reativo termostato sem memória

def percepcao():
    """Lê a temperatura atual do ambiente (simula via input do utilizador)"""
    temp_str = input("Temperatura atual do ambiente: (digite um numero ou sair) ")
    return temp_str

def pensar(entrada):
    """Decide a ação com base na leitura.
    Retorna: ação (string) e temperatura (float ou none)."""
    if entrada.lower() == "sair":
        return 'sair', None

    try:
        temperatura = float(entrada)
    except ValueError:
        print(" Entrada inválida, tente novamente.")
        return 'invalida', None

    if temperatura < 20:
        acao = 'ligar aquecedor'
    elif temperatura > 26.0:
        acao = 'ligar resfriador'
    else:
        acao = 'manter desligado'
    
    return acao, temperatura

def agir(acao, temperatura=None):
    """Executa a ação decidida."""
    if acao == 'sair':
        print("Agente encerrado. Até logo!")
        return False # Encerra o loop principal
    elif acao == 'invalida':
        return True # Continua o loop principal, mas não imprime nada
    else:
        print(f" Temperatura: {temperatura:.1f}°C -> Ação: {acao}")
        return True # Continua o loop principal, imprimindo a ação

def executar_agente():
    """Loop principal do agente: percebe, pensa, age."""
    print("Agente de termostato iniciado. (Digite 'sair' para encerrar )\n")
    while True:
        entrada = percepcao() # Percepção
        acao, temperatura = pensar(entrada) # Pensa e decide
        continuar = agir(acao, temperatura) # Age
        if not continuar: # Se a ação foi 'sair' ou 'invalida', encerra o loop
            break

if __name__ == "__main__":
    executar_agente()