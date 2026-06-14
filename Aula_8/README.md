# FASE 8 - Aula 8: Base de dados de receita pessoal

Vamos criar uma ferramenta que permite ao agente consultar um ficheiro **receitas.json** com as suas receitas favoritas. No final, o agente podera pesquisar uma receita pelo nome e obter ingredientes e passos.

## O que vamos fazer

1. criar o ficheiro **receitas.json** com algumas receitas.

2. Adicionar o método **consultar_receitas** na classe base.

3. Atualizar o prompt, o extrator e o executor para reconhecer a nova ferramenta.

4. Testar com uma pergunta que peça uma receita especifica.

## Passo 1 - Criar o ficheiro **receitas.json**

Na mesma pasta do seu projeto, crie um ficheiro chamado receita.json com este conteúdo (pode acrescentar as suas receitas favoritas).
```python
    [
        {
            "nome": "Bolo de Chocolate",
            "porcoes": 8,
            "ingredientes": {
            "farinha": "200g",
            "açúcar": "150g",
            "ovos": "3",
            "chocolate em pó": "50g",
            "manteiga": "100g"
            },
            "passos": [
            "Misturar farinha, açúcar e chocolate.",
            "Adicionar ovos e manteiga derretida.",
            "Assar em forno pré-aquecido a 180°C por 30 minutos."
            ]
        },
        {
            "nome": "Salada Caesar",
            "porcoes": 4,
            "ingredientes": {
            "alface romana": "1 pé",
            "frango grelhado": "200g",
            "queijo parmesão": "50g",
            "croutons": "100g",
            "molho caesar": "100ml"
            },
            "passos": [
            "Lavar e cortar a alface.",
            "Grelhar o frango e fatiar.",
            "Misturar todos os ingredientes e servir com o molho."
            ]
        }
    ]
```
### Explicação

É uma lista de objetos. Cada receita tem um nome, o número de porções, os ingredientes (dicionário) e uma lista de passos. O agente vai procurar pelo nome.

## Passo 2 - Adicionar o método consultar receita  na classe base

Na classe ferramenta, adicione o método dentro da classe (por exemplo, depois do definir termo).
```python
    def consultar_receita(self, nome: str) -> str:
        """Procura uma receita pelo nome no ficheiro receitas.json e devolve os dados."""
        try:
            with open("receitas.json", "r", encoding="utf-8") as f:
                receitas = json.load(f)
            # Percorre as receitas e verifica se o nome contém a palavra pesquisada
            for receita in receitas:
                if nome.lower() in receita["nome"].lower():
                    texto = f"Receita: {receita['nome']}\n"
                    texto += f"Porções: {receita['porcoes']}\n"
                    texto += "Ingredientes:\n"
                    for ingrediente, quantidade in receita["ingredientes"].items():
                        texto += f"  - {ingrediente}: {quantidade}\n"
                    texto += "Passos:\n"
                    for i, passo in enumerate(receita["passos"], 1):
                        texto += f"  {i}. {passo}\n"
                    return texto.strip()
            return f"Nenhuma receita encontrada com o nome '{nome}'."
        except FileNotFoundError:
            return "Erro: ficheiro receitas.json não encontrado."
        except json.JSONDecodeError:
            return "Erro: ficheiro receitas.json está mal formatado."
        except Exception as e:
            return f"Erro ao consultar receita: {e}"
```
### Explicação detalhada:

+ with open(...) as f: abre o ficheiro de forma segura (fecha automaticamente no final).

+ json.load(f) transforma o texto JSON numa lista de dicionários Python.

+ O for percorre as receitas. Se o nome pedido aparecer no nome da receita (case insensitive), formatamos um texto legível com todos os detalhes.

+ Tratamos erros comuns: ficheiro não encontrado, JSON inválido, etc.

## Passo 3 - Ensinar ao modelo a pedir essa ferramenta

Temos de fazer três atualizações.

a) No system prompt  - adicione a nova instrução:
```python
    "Se precisar de uma receita da sua base de dados pessoal, responda EXATAMENTE neste formato:\n"
    '{"tool": "receita", "nome": "nome da receita"}\n'
```

b) No _extrair_tool - adicione "receita" à lista de ferramentas válidas.
```python
    if obj["tool"] in ["calculadora", "conversor", "pesquisar", "dicionario", "receita"]:
```

c) No _executar_ferramenta - adicione o elif correspondente.
```python
    elif tool_obj["tool"] == "receita":
        return self.consultar_receita(tool_obj["nome"])
```

## Passo 4 - Testar

No ficheiro de teste (teste_receita.py), escreva.
```python
    from AgenteFerramenta_5 import AgenteFerramenta_5

    agente = AgenteFerramenta_5()
    acao, conteudo = agente.pensar("Quero fazer o Bolo de Chocolate da minha base de dados.")
    print("Resposta final:", conteudo)
```
Execute e veja se o agente pede a ferramenta receita e depois apresenta os ingredientes e passos.


## O multiagent 7 

Agora que a consulta funciona, queremos que o agente adicione novas receitas ao ficheiro. É um desafio mais avançado, mas totalmente fazível com o que já sabe.

Objetivo do exercício
Criar uma ferramenta adicionar_receita que permita ao modelo guardar uma nova receita no ficheiro receitas.json.

### Como fazer
1. Criar o método adicionar_receita na classe base

O método receberá o nome, porções, ingredientes e passos. Como o modelo pode ter dificuldade em gerar um JSON complexo com ingredientes (que é um dicionário dentro do JSON), vamos simplificar: os ingredientes e passos virão como strings, e o nosso código trata de os separar.

Formato do JSON que o modelo enviará:

```json
    {
    "tool": "adicionar_receita",
    "nome": "Panquecas Americanas",
    "porcoes": 4,
    "ingredientes": "farinha:200g, leite:300ml, ovos:2, açúcar:30g",
    "passos": "Misturar tudo|Aquecer frigideira|Cozinhar 2 min de cada lado"
    }
```

Método sugerido:

```python
    def adicionar_receita(self, nome: str, porcoes: int, ingredientes_str: str, passos_str: str) -> str:
        """Adiciona uma nova receita ao ficheiro receitas.json."""
        try:
            # Converter a string de ingredientes em dicionário
            ingredientes = {}
            for item in ingredientes_str.split(","):
                if ":" in item:
                    chave, valor = item.split(":", 1)
                    ingredientes[chave.strip()] = valor.strip()
            
            # Converter a string de passos em lista
            passos = [p.strip() for p in passos_str.split("|") if p.strip()]
            
            nova_receita = {
                "nome": nome,
                "porcoes": int(porcoes),
                "ingredientes": ingredientes,
                "passos": passos
            }
            
            # Carregar receitas existentes
            try:
                with open("receitas.json", "r", encoding="utf-8") as f:
                    receitas = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                receitas = []
            
            # Verificar se já existe uma receita com o mesmo nome
            for r in receitas:
                if r["nome"].lower() == nome.lower():
                    return f"A receita '{nome}' já existe na base de dados."
            
            receitas.append(nova_receita)
            with open("receitas.json", "w", encoding="utf-8") as f:
                json.dump(receitas, f, ensure_ascii=False, indent=2)
            
            return f"Receita '{nome}' adicionada com sucesso!"
        except Exception as e:
            return f"Erro ao adicionar receita: {e}"
```

2. Adicionar ao prompt

```python
    "Se precisar de guardar uma nova receita na base de dados, responda EXATAMENTE neste formato:\n"
    '{"tool": "adicionar_receita", "nome": "...", "porcoes": número, "ingredientes": "ingrediente:quantidade, ...", "passos": "passo1|passo2|..."}\n'
```

3. Atualizar _extrair_tool e _executar_ferramenta

Acrescente "adicionar_receita" em ambas.

No executor:

```python
    elif tool_obj["tool"] == "adicionar_receita":
        return self.adicionar_receita(
            tool_obj["nome"],
            tool_obj.get("porcoes", 2),
            tool_obj.get("ingredientes", ""),
            tool_obj.get("passos", "")
        )
```

4. Testar

Pergunte algo como: "Adiciona à minha base uma receita de Panquecas Americanas para 4 pessoas." O agente deverá gerar o JSON de adição e confirmar o sucesso. Depois pode pedir para consultar a receita que acabou de adicionar.

