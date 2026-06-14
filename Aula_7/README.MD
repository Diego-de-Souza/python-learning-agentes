# FASE 7 - AULA 7: Dar ao agente o opder de pesquisar na internet

Até agora o agente estáva limitado ao conhecimento interno do modelo e às ferramentas que nós programamos (calculadora, conversor). Nesta aula vamos dar-lhe um novo sentido: a capacidade de pesquisar informações atualizadas na web. Ele poderá procurar receitas, preços, substitutos de ingredientes, etc.

## Conceito

Uma ferramenta de pesquisa funciona assim:

1. O modelo percebe que precisa da informação externa.

2. Devolve um json especial, ex.: {"tool": "pesquisar", "consulta": "receita de lasanha vegetariana"}.

3. O código detecta o JSON, chama uma função python que pesquisa na web e devolve os resultados.

4. O modelo recebe o resultado e continua seu trabalho.

## Instalação

no terminal execute:
```powershell
    pip install duckduckgo-search
```

## Passo 1: adicionar o metodo de pesquisa no AgenteFerramenta

Abra o ficheiro AgenteFerramenta.py (a classe base) e acrescente este método.
```powershell
    from duckduckgo_search import DDGS

def pesquisar_web(self, consulta: str, max_resultados: int = 3) -> str:
    """
    Pesquisa na web usando DuckDuckGo e devolve um resumo dos resultados.
    """
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(consulta, max_results=max_resultados))
            if not resultados:
                return "Nenhum resultado encontrado para esta pesquisa."
            
            linhas = []
            for i, r in enumerate(resultados, 1):
                titulo = r.get('title', 'Sem título')
                corpo = r.get('body', '')
                # Limita o tamanho do corpo para não encher o histórico
                corpo_resumido = corpo[:200] + "..." if len(corpo) > 200 else corpo
                linhas.append(f"{i}. {titulo}\n   {corpo_resumido}")
            
            return "\n\n".join(linhas)
    except Exception as e:
        return f"Erro ao pesquisar na web: {e}"
```

### explicação sobre cada linha

+ DDGS() cria um cliente de pesquisa (funciona como um gestor de contexto, with garante que é fechado).

+ ddgs.text(consulta, max_results=max_resultados) devolve um gerador com resultados. Convertermos para lista.

+ Cada resultado tem title (título) e body (descrição). Limitamos o corpo a 200 caracteres.

+ Se algo correr mal (ex.: sem internet), capturamos a exceção e devolvemos uma mensagem de erro amigavel.


## Passo 2 -  ensinar o modelo a pedir a pesquisa

No **__init__**  do AgenteFerramenta, acrescente ao **system_prompt_base** a instrução para nova ferramenta. Isto é crucial: o modelo só usara a ferramenta se souber que ela existe e qual o formato exato.

Adicione esta linha ao texto do prompt (logo a seguir às instruções do conversor):
```porwershel
    "Se precisar de pesquisar na internet, responda EXATAMENTE neste formato (e mais nada):\n"
    '{"tool": "pesquisar", "consulta": "a sua pergunta"}\n'
```

## Passo 3 - Atualizar o extrato e o executor de ferramentas

Ainda no AgenteFerramenta.py:

No método _extrair_tool, adicione "pesquisar" á a lista de ferramentasválidas:
```python
    if obj["tool"] in ["calculadora", "conversor", "pesquisar"]:
        return obj, json_str
```

No método _executar_ferramenta, acrescente o novo caso:
```python
    elif tool_obj["tool"] == "pesquisar":
        return self.pesquisar_web(tool_obj["consulta"])
```

## Passo 4 - Testar nova ferramenta

Vamos fazer um teste rápido e isolado.Crie um ficheiro temporario teste_pesquisa.py:
```python
    from AgenteFerramenta import AgenteFerramenta
    import openai

    client = openai.OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    modelo = "qwen2.5:3b"

    agente = AgenteFerramenta(client, modelo)
    agente.mensagens = [{"role": "system", "content": agente.system_prompt_base}]
    agente.mensagens.append({"role": "user", "content": "Quanto custa 1kg de farinha no Brasil hoje?"})

    # Chama o ciclo pensar (que agora inclui a possibilidade de pesquisa)
    acao, conteudo = agente.pensar("Quanto custa 1kg de farinha no Brasil hoje?")
    print(conteudo)
```

Execute e veja se o agente pede a feramenta pesquisar, obtém os resultados e responde com a informação.

## Passo 5 - Integrar no sistema multi-agente

Agora ue a ferramenta está na classe base, tato o executor como qualquer outro agente que herde de AgenteFerramenta terão automaticamente a capacidade de pesquisa.Não é preciso alterar o AgenteExecutor nem o AgentePlanejador.

Execute o agents_main.py com um peido que exija pesquisa, por exemplo:
```python
    "Pesquisa uma receita de pavê de chocolate e calcula os ingredientes para 8 pessoas."
```

O planejador vai incluir um passo de pesquisa. O executor, ao chegar a esse passo, usará uma nova ferramenta.

## A parte de multi-agente 5 é para adição do dicionário

O objetivo é ensinar o agente a conhecer termos culinários sem precisar de ir à internet. Imagine que lhe pergunta:

"O que significa emulsionar?"

Hoje, o agente poderia pesquisar na web, mas isso é lento e gasta recursos. Se tivermos um pequeno dicionário interno com definições, ele responde instantaneamente. O exercício é criar exatamente essa ferramenta.

### O que é um "dicionário interno"?

É uma estrutura de dados em Python do tipo dict, onde a chave é o termo e o valor é a definição. Exemplo:

### O que é um "dicionário interno"?
É uma estrutura de dados em Python do tipo dict, onde a chave é o termo e o valor é a definição. Exemplo:
```python
    self.dicionario = {
        "brunoise": "Corte em cubos muito pequenos (cerca de 2-3 mm).",
        "emulsionar": "Misturar dois líquidos que normalmente não se misturam, como óleo e vinagre, até formar uma mistura estável.",
        "clarificar": "Remover impurezas de um líquido, como caldos ou manteiga, aquecendo e retirando a espuma."
    }
```
Pode acrescentar os termos que quiser. Eu sugiro começar com 5 ou 6.

### O que é o método definir_termo?
É uma função dentro da classe AgenteFerramenta_4 que recebe uma string (o termo a procurar) e retorna a definição (ou uma mensagem de erro). Algo assim:
```python
    def definir_termo(self, termo: str) -> str:
    termo = termo.lower().strip()
    definicao = self.dicionario.get(termo)
    if definicao:
        return f"{termo}: {definicao}"
    else:
        return f"O termo '{termo}' não está no meu dicionário."
```
Porquê este método? Porque a estrutura _executar_ferramenta precisa de chamar uma função para cada tipo de ferramenta. definir_termo é a função que trata do "dicionario".

