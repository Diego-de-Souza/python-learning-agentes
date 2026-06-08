# FASE 2 - Aula 2 : Agentes com estado de memória

## O que é um agente com estado?

Na aula nterior foi criado uma agende reativo, a cada ciclo ele olhada apenas para entrada, decidia e agia, sem se lembrar do que aconteceu antes.

Um agente com estado (ou com memória) guarda internamente informações sobre o passado e usa essas informações para decidir melhor o futuro. Essa mémória interna cham-se de estado.

Exemplo simples:

- Um termostato que lembra se o aquecedor já está ligado, para evitar ligar e desligar a cada segundo (histerese).
- Um semafaro que conta quantos carros passaram desde a ultima vez que o sinal abriu para pedestres.
- Um robo que sabe sua posição atual e decide para onde ir a seguir.

Agora vamos evoluir o termostato da aula anterior, adicionando histerese: ele só liga o aquecedor se a temperatura estiver abaixo de 18°C e só desligar quando subir a cima de 21°C. Isso evita que fique "piscando" quando a temperatura está perto do limite.

Vamos também mudar a organização do código: usaremos uma classe para representar o agente. Assim, o estado fica naturalmente guardado nos atributos do objeto.Não se preocupe se você não domina a orientação a objetos, cada parte será explicada.

### O que mudou e porque?

1. classe e estado interno

`__init__` define self.aquecedor_ligado e self.aquecedor_ligado. Essas váriaveis são a memoria do agente. Elas persistem entre um ciclo e outro.

1. histerese

O aquecedor não liga exatamente nos 20°C, mas sim quando cai abaixo de 18°C, e só desliga quando passa dos 21°C. Isso impede que a temperatura oscile entre 19.9 e 20.1 fique ligando e desligando sem parar. O mesmo vale para o resfriador (liga a cima de 26°C, delisga abaixo de 23°C)

1. Comportamento inteligente

O agente agora "sabe" que não deve ligar o resfriador se o aquecedor estiver ligado, e vice-versa.Em qualquer transição, o posto é desligado.

1. impressão mais informativa

A função agir mostra não só a ação, mas também o estado atual dos equipamentos.

## O script 2 é a melhoria do semafaro

Missão:
Transforme o semáforo que você fez no exercício da aula 1 num agente com memória. O agente deve:

Ter um contador interno de quantos carros passaram desde a última vez que o sinal ficou verde para pedestres.

Quando o utilizador escreve "carro":

Se o contador de carros for menor que 3, o agente responde: "🟢 Sinal verde para carros. Pedestres esperam." e incrementa o contador.

Se o contador atingir 3 ou mais, o agente automaticamente deve mudar para o modo pedestre: "🚶‍♂️ Prioridade para pedestres! Sinal vermelho para carros." e reinicia o contador para zero.

Quando o utilizador escreve "pedestre", o agente responde imediatamente: "🚶‍♂️ Prioridade para pedestres! Sinal vermelho para carros." e também zera o contador de carros.

O comando "emergencia" continua a funcionar: 🚨 "Todos param! Trânsito interrompido." (não mexe no contador).

Qualquer outra entrada (exceto "sair") mostra: "Modo normal: sinal fechado para todos." e não altera o contador.

"sair" encerra o agente.