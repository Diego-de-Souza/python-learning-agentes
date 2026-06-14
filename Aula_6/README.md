# Fase 6 - Aula 6: Autonomizar o executor (eliminar o "Enter")

Na Aula 5 o agente ainda precisava do utilizador para duas coisas:
 
 1. Pressionar "Enter" para começar a execução.

 2. Os modelos às vezes esperava confirmação entre passos.

Hoje vamos eliminar essas depêndencias. O executor irá ler o plano, arrancar sozinho, percorrer cada passo e só parar quando o plano estiver concluído.

## O que precisa mudar (e porquê)?

+ Mensagem inicial automática: em vez de esperar que o utilizador escreva "Iniciar plano", o próprio código adiciona uma mensagem **user** com "Comerçar a executar plano".

+ Instrução mais firme ao modelo: o system prompt tem que ser claro: "Não peças confirmação. Apenas executa os passos um de cada vez."

+ Avanço automático entre passos: quando o executor termina um passo e devolve uma resposta (sem ferramentas), o código deve imediatamente pedir "Próximo passo, por favor" para continuar o ciclo.

+ critério de paragem: o modelo dirá "Plano concluído" no final. Quando isso aparecer, o ciclo termina.


## estrutura do método Executar plano autónomo

1. Reiniciamos as mensagens com o system prompt base + uma segunda mensagem de sistema que contem o plano e as instruções.

2. Adicionamos a mensagem de arranque: "Começa a executar o plano."

3. Um ciclo for de até 15 iterações (porque o plano pode ter muitos passos).

4. Dentro do ciclo:

+ Chamamos o SLM (_chamar_slm).

+ Se a resposta for uma ferramenta, executamo‑la e adicionamos o resultado ao histórico.

+ Se for texto:

    + Mostramos um resumo do passo no ecrã.

    + Verificamos se contém "plano concluído" ou "execução finalizada". Se sim, saímos com sucesso.

    + Caso contrário, acrescentamos a mensagem "Próximo passo, por favor." para o modelo continuar.