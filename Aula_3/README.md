# FASE 3 - Aula 3: Agentes com celebro de IA (LLM)

Até aqui, a inteligência do do agente era feito regras escritas por nós (if temperatura < 20, if contador < 3>). Agora vamos subistituir o pensar por um modelo de linguagem como o deepSeek, GPT-4, etc. O agente continuara a perceber, mas a decisão será gerada pela IA com base numa instrução (prompt) e no contexto que lhe dermos.

Esse passo tras a contrução de um agente conversador que usa o LLM para responder ao utilizador. Nas próximas fases será implementado os agentes usando ferramentas.

## O que muda na arquitetura?

```
    Percepção ──> [Prompt + Entrada] ──> LLM ──> Resposta ──> Ação (imprimir)
```

+ A percepção() continua a ler a entrada do utilizador.
+ pensar() agora constrói um prompt com instruções e a entrada, envia para a API do LLM e recebe a resposta.
+ agir() apenas imprime a resposta.


## Pré-requisitos

1. Python com o pacote openai instalado.
```
    pip install openai
```
2. Uma chave de API de um fornecedor de LLM. Vou usar o deepSeek como exemplo (porque oferece um periodo gratuito e é muito acessível), mas o código é quase idêntico para o OpenAI, Grok e etc.
    + Crie uma conta em [platform.deepseek.com](https://platform.deepseek.com/sign_in) 
    + Gere uma chave de api no painel.
    + Nunca cooloque diretamente no código! Vamos guarda-la numa váriavel de ambiente chamada DEEPSEEK_API-KEY.

No terminal:
(linux / MAC)
```terminal
    export DEEPSEEK_API_KEY="sk-..."
```

(porwershell)
```porwershell
    $env:DEEPSEEK_API_KEY="sk-..."
```

Ou crie um ficheiro .env (opcional, mas mais seguro).

3. (Opcional) Se preferir usar outro provedor, basta mudar a base_url e o nome do modelo. Para OpenAI seria api.openai.com e modelo gpt-3.5-turbo. A estrutura é a mesma.


## explicação detalhada

+ Cliente OpenAI: Mesmo usando o DeepSeek, o pacote openai reconhece a base_url alternativa. O código funcionaria igual com OpenAI trocando apenas a URL e o modelo.

+ Histórico self.mensagens: O agente mantém toda a conversa (memória de longo prazo) para que o LLM saiba o contexto. A primeira mensagem é o system, que define a personalidade.

+ pensar agora envia todo o histórico para a API e devolve a resposta. Em caso de erro, captura a exceção e mantém o loop.

+ Segurança da chave: O código lê a chave de os.environ. É essencial nunca a escrever diretamente no ficheiro. Se quiser uma alternativa mais robusta, podemos usar python-dotenv para ler de um .env.

+ Custos: O DeepSeek tem preços muito reduzidos, mas fique atento ao consumo. Pode definir max_tokens para limitar.

### Execute o experimento

Após definir a variavel de ambiente execute:
```terminal
    py agente_llm.py
```
Converse livremente. O agente responde com a inteligência do modelo. Repare que ele memoriza o contexto da conversa.


## Segundo script é um script de agente especialista em culinária

Agora quero que dê um passo além: transforme o agente num assistente especializado em receitas culinárias.

Modifique a mensagem de system para algo como:
"Você é um chef de cozinha experiente. Dê receitas baseadas nos ingredientes que o utilizador indicar. Se o utilizador não fornecer ingredientes, pergunte o que ele quer cozinhar. Seja criativo e dê instruções passo a passo."

Adicione ao código um “atalho” manual (sem LLM) para comandos especiais:

Se o utilizador escrever "dica", o agente não chama o LLM; em vez disso, devolve imediatamente uma dica culinária aleatória pré‑definida (pode usar uma lista de dicas e escolher uma com random.choice).

Se o utilizador escrever "compras", o agente também ignora o LLM e devolve uma mensagem a listar os ingredientes da última receita que ele sugeriu (para isso terá de guardar a última receita numa variável self.ultima_receita – que será atualizada sempre que o LLM responder com uma receita; pode detetar se a resposta contém “receita” ou “ingredientes” e guardar o texto).

Mantenha o comando "sair".

Isto obriga‑o a misturar regras fixas com LLM, preparando‑o para a próxima aula onde vamos dar ferramentas ao agente.