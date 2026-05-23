# Mapa de Integração Backend - Tele Severino

Este documento mostra onde o backend deve olhar no código do frontend para integrar API e banco MySQL.

O objetivo é ajudar o dev backend a entender:

- Onde estão os dados mockados.
- Onde as telas buscam os dados.
- Onde substituir mock por banco/API.
- Qual arquivo mexer para cada fluxo.
- Quais tabelas e endpoints são necessários.

---

## 1. Visão geral da arquitetura

O projeto está organizado em camadas:

```text
Tela HTML
↓
routes
↓
services
↓
repositories
↓
data.py atualmente
↓
MySQL futuramente
```

Hoje o projeto usa mocks em:

```text
app/data.py
```

No futuro, o backend deve substituir os mocks por consultas reais ao MySQL dentro da camada:

```text
app/repositories/
```

A regra principal é:

```text
routes não acessa banco diretamente.
services concentram regra de negócio.
repositories acessam o MySQL ou API.
```

---

## 2. Estrutura principal do projeto

```text
app/
├── routes/
├── services/
├── repositories/
├── models/
├── templates/
├── static/
├── config.py
├── database.py
└── data.py
```

### Responsabilidade de cada pasta

```text
routes
Controla as URLs e renderiza as telas.

services
Concentra regras de negócio.

repositories
Ponto correto para integrar banco MySQL ou API.

models
Referência das tabelas futuras.

templates
Arquivos HTML das telas.

static
CSS e JavaScript.

data.py
Dados mockados temporários.
```

---

## 3. Arquivo principal para rodar o projeto

```text
run.py
```

Este arquivo inicia o Flask.

Comando para rodar:

```bash
python run.py
```

Aplicação local:

```text
http://127.0.0.1:5000
```

---

## 4. Configuração do banco

Arquivo:

```text
app/config.py
```

Hoje existe uma variável preparada para MySQL:

```python
MYSQL_DATABASE_URL = os.getenv(
    "MYSQL_DATABASE_URL",
    "mysql://usuario:senha@localhost:5432/tele_severino"
)
```

Quando o banco real existir, configurar via `.env`:

```text
MYSQL_DATABASE_URL=mysql://usuario:senha@localhost:5432/tele_severino
```

---

## 5. Conexão com MySQL

Arquivo:

```text
app/database.py
```

Este arquivo deve centralizar a conexão com o banco.

Exemplo futuro usando mysql-connector-python:

```python
import mysql-connector-python
from flask import current_app

def get_db_connection():
    return mysql-connector-python.connect(current_app.config["MYSQL_DATABASE_URL"])
```

Ou usando SQLAlchemy:

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

O dev backend pode escolher a abordagem.

---

## 6. Onde estão os mocks atuais

Arquivo:

```text
app/data.py
```

Esse arquivo contém listas como:

```python
CATEGORIES = [...]
SPECIALISTS = [...]
```

Esses dados são temporários.

Quando o backend estiver pronto, os repositories devem parar de importar dados de `app.data`.

Exemplo atual:

```python
from app.data import SPECIALISTS

def list_specialists():
    return SPECIALISTS
```

Exemplo futuro:

```python
def list_specialists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM specialists WHERE is_online = true")
    specialists = cursor.fetchall()
    conn.close()
    return specialists
```

---

# 7. Mapa por fluxo

---

## 7.1 Login e cadastro

### Telas

```text
/login
/cadastro
```

### Templates

```text
app/templates/login.html
app/templates/cadastro.html
```

### Routes

```text
app/routes/auth_routes.py
```

### Service

```text
app/services/auth_service.py
```

### Repository

```text
app/repositories/user_repository.py
```

### O que integrar

O backend deve implementar:

```text
Cadastro de usuário
Login
Busca por e-mail
Validação de senha
Sessão ou token
```

### Tabela sugerida

```text
users
- id
- name
- email
- password_hash
- account_type
- created_at
```

### Endpoints sugeridos

```text
POST /api/auth/login
POST /api/auth/register
GET  /api/auth/me
```

### Pontos de atenção

A senha nunca deve ser salva pura.

Usar hash de senha.

Exemplo:

```python
from werkzeug.security import generate_password_hash, check_password_hash
```

---

## 7.2 Home e categorias

### Tela

```text
/home
```

### Template

```text
app/templates/home.html
```

### Route

```text
app/routes/main_routes.py
```

### Repository

```text
app/repositories/category_repository.py
```

### Dados mockados atuais

```text
app/data.py
```

Lista usada:

```python
CATEGORIES
```

### O que integrar

O backend deve buscar as categorias no MySQL.

### Tabela sugerida

```text
categories
- id
- slug
- name
- icon
- tone
```

### Endpoint sugerido

```text
GET /api/categories
```

### Função onde trocar o mock

Arquivo:

```text
app/repositories/category_repository.py
```

Função:

```python
def list_categories():
    return CATEGORIES
```

Trocar por consulta real no MySQL.

---

## 7.3 Lista de especialistas

### Telas

```text
/especialistas
/especialistas?categoria=tecnologia
/especialistas?categoria=construcao
```

### Template

```text
app/templates/especialistas.html
```

### Route

```text
app/routes/specialist_routes.py
```

### Service

```text
app/services/specialist_service.py
```

### Repository

```text
app/repositories/specialist_repository.py
```

### Dados mockados atuais

```text
app/data.py
```

Lista usada:

```python
SPECIALISTS
```

### O que integrar

O backend deve permitir:

```text
Listar especialistas online
Filtrar por categoria
Buscar especialista por ID
Buscar preço por minuto
Buscar avaliação
Buscar quantidade de avaliações
```

### Tabela sugerida

```text
specialists
- id
- user_id
- name
- role
- category_slug
- rating
- reviews_count
- price_per_minute
- about
- is_online
- avatar_url
```

### Endpoints sugeridos

```text
GET /api/specialists
GET /api/specialists?category=tecnologia
GET /api/specialists/{id}
```

### Funções onde trocar o mock

Arquivo:

```text
app/repositories/specialist_repository.py
```

Funções:

```python
def list_specialists():
    return SPECIALISTS

def list_home_specialists():
    return SPECIALISTS[:3]

def list_specialists_by_category(category_slug):
    return [item for item in SPECIALISTS if item["category"] == category_slug]

def get_specialist_by_id(specialist_id):
    return next((item for item in SPECIALISTS if item["id"] == specialist_id), SPECIALISTS[0])
```

Essas funções devem passar a consultar MySQL.

---

## 7.4 Perfil do especialista

### Tela

```text
/especialista/1
```

### Template

```text
app/templates/perfil.html
```

### Route

```text
app/routes/specialist_routes.py
```

### Service

```text
app/services/specialist_service.py
```

### Repository

```text
app/repositories/specialist_repository.py
```

### O que integrar

O backend deve buscar:

```text
Dados do especialista
Especialidades/tags
Avaliações
Preço por minuto
Média de avaliação
Quantidade de avaliações
```

### Tabela complementar sugerida

```text
specialist_tags
- id
- specialist_id
- name
```

### Endpoint sugerido

```text
GET /api/specialists/{id}
GET /api/specialists/{id}/reviews
```

---

## 7.5 Chamada

### Tela

```text
/chamada/1
```

### Template

```text
app/templates/chamada.html
```

### Route

```text
app/routes/call_routes.py
```

### Service

```text
app/services/call_service.py
```

### Repository

```text
app/repositories/call_repository.py
```

### O que integrar

O backend deve implementar:

```text
Iniciar chamada
Registrar horário inicial
Finalizar chamada
Registrar horário final
Calcular tempo total
Calcular valor final
Atualizar status da chamada
```

### Tabela sugerida

```text
calls
- id
- user_id
- specialist_id
- started_at
- ended_at
- total_seconds
- total_value
- status
```

### Status sugeridos

```text
in_progress
finished
cancelled
failed
```

### Endpoints sugeridos

```text
POST /api/calls/start
POST /api/calls/{id}/finish
GET  /api/calls/{id}
```

### Ponto importante

Hoje o cronômetro na tela é apenas visual e fica no JavaScript:

```text
app/static/script.js
```

O cálculo real de tempo e valor deve ser feito no backend, não no frontend.

---

## 7.6 Pagamento

### Tela

```text
/pagamento/1
```

### Template

```text
app/templates/pagamento.html
```

### Route

```text
app/routes/payment_routes.py
```

### Service

```text
app/services/payment_service.py
```

### Repository

```text
app/repositories/payment_repository.py
```

### O que integrar

O backend deve implementar:

```text
Buscar resumo da chamada
Buscar tempo total
Buscar valor por minuto
Calcular valor final
Criar pagamento
Confirmar pagamento
Atualizar status
```

### Tabela sugerida

```text
payments
- id
- user_id
- specialist_id
- call_id
- amount
- method
- status
- created_at
- paid_at
```

### Métodos sugeridos

```text
credit_card
pix
```

### Status sugeridos

```text
pending
paid
failed
cancelled
```

### Endpoints sugeridos

```text
POST /api/payments
POST /api/payments/{id}/confirm
GET  /api/payments/{id}
```

### Ponto importante

O valor final do pagamento deve vir do backend.

Não confiar no valor calculado pelo frontend.

---

## 7.7 Avaliação

### Tela

```text
/avaliacao/1
```

### Template

```text
app/templates/avaliacao.html
```

### Route

```text
app/routes/review_routes.py
```

### Service

```text
app/services/review_service.py
```

### Repository

```text
app/repositories/review_repository.py
```

### O que integrar

O backend deve implementar:

```text
Salvar nota
Salvar comentário
Vincular avaliação ao usuário
Vincular avaliação ao especialista
Vincular avaliação à chamada
Atualizar média do especialista
```

### Tabela sugerida

```text
reviews
- id
- user_id
- specialist_id
- call_id
- rating
- comment
- created_at
```

### Endpoints sugeridos

```text
POST /api/reviews
GET  /api/specialists/{id}/reviews
```

### Regra importante

A avaliação só deve ser permitida se:

```text
Chamada finalizada
Pagamento confirmado
Usuário participou da chamada
```

---

## 7.8 Personalização da marca

### Tela

```text
/personalizacao
```

### Template

```text
app/templates/personalizacao.html
```

### Route

```text
app/routes/brand_routes.py
```

### Service

```text
app/services/platform_service.py
```

### Repository

```text
app/repositories/platform_repository.py
```

### O que integrar

O backend deve permitir:

```text
Buscar nome da plataforma
Buscar cor principal
Buscar logo
Salvar nome
Salvar cor
Salvar logo
```

### Tabela sugerida

```text
platform_settings
- id
- platform_name
- primary_color
- logo_url
- updated_at
```

### Endpoints sugeridos

```text
GET /api/platform-settings
PUT /api/platform-settings
```

---

# 8. Ordem sugerida para o backend implementar

Sugestão de ordem para facilitar:

```text
1. Configurar conexão com MySQL
2. Criar tabela users
3. Implementar cadastro
4. Implementar login
5. Criar tabela categories
6. Criar tabela specialists
7. Substituir mocks de categorias e especialistas
8. Criar tabela calls
9. Implementar início e fim de chamada
10. Criar tabela payments
11. Implementar pagamento
12. Criar tabela reviews
13. Implementar avaliação
14. Criar tabela platform_settings
15. Implementar personalização da marca
```

---

# 9. Arquivos que o dev backend deve começar lendo

Começar por estes arquivos:

```text
README.md
docs/MAPA_INTEGRACAO_BACKEND.md
docs/BACKEND_INTEGRATION.md
app/data.py
app/repositories/category_repository.py
app/repositories/specialist_repository.py
app/repositories/user_repository.py
app/repositories/call_repository.py
app/repositories/payment_repository.py
app/repositories/review_repository.py
app/repositories/platform_repository.py
app/database.py
app/config.py
```

---

# 10. Resumo para o dev backend

O frontend já está separado para receber backend.

Hoje os dados estão mockados em:

```text
app/data.py
```

O backend deve substituir os mocks dentro de:

```text
app/repositories/
```

Fluxo esperado:

```text
routes → services → repositories → MySQL
```

Evitar:

```text
HTML acessando banco
routes acessando banco direto
frontend calculando valores finais
senha salva sem hash
```

Fazer:

```text
repositories consultam banco
services validam regras
routes renderizam telas
backend calcula tempo e valor da chamada
backend confirma pagamento
backend valida permissão de avaliação
```
