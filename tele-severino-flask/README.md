# Tele Severino - Protótipo Flask

Projeto em Python + Flask + HTML + CSS para simular as telas do Tele Severino.

## Como rodar no VS Code

```bash
cd tele-severino-flask
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

## Telas criadas

- `/inicio` - tela laranja de carregamento
- `/login` - login
- `/cadastro` - criar conta
- `/home` - tela inicial
- `/personalizacao` - personalização da marca
- `/especialistas` - lista de especialistas
- `/especialistas?categoria=construcao` - especialistas por categoria
- `/especialista/1` - perfil do especialista
- `/chamada/1` - chamada em andamento
- `/pagamento/1` - pagamento
- `/avaliacao/1` - avaliação

## Pontos de integração futura

O arquivo `app.py` está comentado com os locais onde entram:

- Backend de autenticação
- Banco MySQL
- Cadastro de usuário
- Lista de categorias
- Lista de especialistas
- Pagamento
- Chamada
- Avaliação

---

## Documentação para integração backend

Para o dev backend entender onde integrar API e MySQL, ler primeiro:

```text
docs/MAPA_INTEGRACAO_BACKEND.md
```

Esse arquivo mostra:

- Onde estão os dados mockados.
- Quais repositories precisam ser alterados.
- Quais tabelas são sugeridas.
- Quais endpoints a API deve fornecer.
- Qual fluxo cada tela usa.
- Onde integrar MySQL no código.

Documentação complementar:

```text
docs/BACKEND_INTEGRATION.md
docs/GUIA_BACKEND_JUNIOR.md
```
