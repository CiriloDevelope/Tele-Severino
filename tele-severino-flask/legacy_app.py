from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ============================================================
# PONTO DE INTEGRAÇÃO COM BACKEND + BANCO POSTGRESQL
# ============================================================
# Hoje estes dados estão mockados em listas Python para facilitar
# a apresentação no VS Code.
#
# Quando integrar com backend real + PostgreSQL, a ideia é:
#
# 1. Criar uma conexão com o banco PostgreSQL usando SQLAlchemy ou psycopg2.
#    Exemplo de variáveis que viriam do .env:
#
#    DATABASE_URL=postgresql://usuario:senha@localhost:5432/tele_severino
#
# 2. Trocar as listas CATEGORIES e SPECIALISTS por consultas no banco:
#
#    SELECT * FROM categories;
#    SELECT * FROM specialists;
#    SELECT * FROM users;
#    SELECT * FROM reviews;
#    SELECT * FROM calls;
#    SELECT * FROM payments;
#
# 3. Rotas que hoje apenas redirecionam, como /login e /cadastro,
#    deverão chamar o backend de autenticação.
#
# 4. Rotas como /pagamento, /chamada e /avaliacao deverão salvar dados:
#
#    calls: histórico da chamada, tempo, valor por minuto e total.
#    payments: forma de pagamento, status e valor.
#    reviews: nota, comentário e especialista avaliado.
#
# 5. Cada especialista poderá vir do banco filtrado pela categoria:
#
#    SELECT * FROM specialists WHERE category_slug = 'tecnologia';
#
# Mantive comentários nos pontos principais abaixo para indicar
# exatamente onde encaixar as integrações futuramente.
# ============================================================


CATEGORIES = [
    {"slug": "eletrica", "name": "Elétrica", "icon": "⚡", "tone": "yellow"},
    {"slug": "tecnologia", "name": "Tecnologia", "icon": "◌", "tone": "blue"},
    {"slug": "construcao", "name": "Construção", "icon": "⌁", "tone": "orange"},
    {"slug": "culinaria", "name": "Culinária", "icon": "✂", "tone": "red"},
    {"slug": "estudos", "name": "Estudos", "icon": "□", "tone": "green"},
    {"slug": "design", "name": "Design", "icon": "◉", "tone": "purple"},
]

SPECIALISTS = [
    {
        "id": 1,
        "name": "Ana Souza",
        "role": "Desenvolvedora",
        "category": "tecnologia",
        "rating": "4.9",
        "reviews": 203,
        "price": "5.00",
        "about": "Desenvolvedora full-stack com 10 anos de experiência. Especialista em React, Node.js e soluções em nuvem.",
        "tags": ["Desenvolvimento web", "React e Node.js", "Cloud computing", "Arquitetura de software"],
        "initials": "AS",
        "avatar_class": "avatar-1",
    },
    {
        "id": 2,
        "name": "Rafael Lima",
        "role": "Infraestrutura",
        "category": "tecnologia",
        "rating": "4.8",
        "reviews": 156,
        "price": "4.80",
        "about": "Especialista em redes, servidores, cloud e suporte para pequenas empresas.",
        "tags": ["Redes", "Servidores", "Cloud", "DevOps"],
        "initials": "RL",
        "avatar_class": "avatar-2",
    },
    {
        "id": 3,
        "name": "Carlos Mendes",
        "role": "Suporte Técnico",
        "category": "tecnologia",
        "rating": "4.7",
        "reviews": 189,
        "price": "3.80",
        "about": "Atendimento técnico rápido para computadores, sistemas e dúvidas digitais.",
        "tags": ["Suporte técnico", "Windows", "Hardware"],
        "initials": "CM",
        "avatar_class": "avatar-3",
    },
    {
        "id": 4,
        "name": "João Pedro",
        "role": "Eletricista Residencial",
        "category": "eletrica",
        "rating": "4.9",
        "reviews": 224,
        "price": "4.50",
        "about": "Especialista em instalações residenciais, tomadas, quadros e manutenção elétrica.",
        "tags": ["Instalação elétrica", "Quadro de energia", "Manutenção"],
        "initials": "JP",
        "avatar_class": "avatar-4",
    },
    {
        "id": 5,
        "name": "Marcos Silva",
        "role": "Instalações",
        "category": "eletrica",
        "rating": "4.8",
        "reviews": 167,
        "price": "4.20",
        "about": "Atua com instalações, revisões e adequações elétricas de baixa tensão.",
        "tags": ["Instalações", "Baixa tensão", "Revisão elétrica"],
        "initials": "MS",
        "avatar_class": "avatar-5",
    },
    {
        "id": 6,
        "name": "Felipe Costa",
        "role": "Designer",
        "category": "design",
        "rating": "4.7",
        "reviews": 131,
        "price": "4.00",
        "about": "Ajuda com identidade visual, layout, apresentações e materiais digitais.",
        "tags": ["UI Design", "Identidade visual", "Figma"],
        "initials": "FC",
        "avatar_class": "avatar-6",
    },
    {
        "id": 7,
        "name": "Pedro Santos",
        "role": "Engenheiro Civil",
        "category": "construcao",
        "rating": "4.9",
        "reviews": 156,
        "price": "4.00",
        "about": "Consultoria para pequenas obras, reformas e dúvidas estruturais.",
        "tags": ["Construção", "Reforma", "Obra residencial"],
        "initials": "PS",
        "avatar_class": "avatar-7",
    },
    {
        "id": 8,
        "name": "Bianca Rocha",
        "role": "Professora",
        "category": "estudos",
        "rating": "4.8",
        "reviews": 118,
        "price": "3.50",
        "about": "Apoio para estudos, organização, trabalhos acadêmicos e reforço escolar.",
        "tags": ["Reforço", "Organização", "Trabalhos"],
        "initials": "BR",
        "avatar_class": "avatar-8",
    },
    {
        "id": 9,
        "name": "Nina Alves",
        "role": "Chef de cozinha",
        "category": "culinaria",
        "rating": "4.9",
        "reviews": 142,
        "price": "4.30",
        "about": "Consultoria para receitas, cardápios, preparo e técnicas simples de cozinha.",
        "tags": ["Receitas", "Cardápio", "Cozinha prática"],
        "initials": "NA",
        "avatar_class": "avatar-9",
    },
]


def get_specialist(specialist_id):
    # Futuro PostgreSQL:
    # SELECT * FROM specialists WHERE id = specialist_id;
    return next((item for item in SPECIALISTS if item["id"] == specialist_id), SPECIALISTS[0])


def category_name(slug):
    # Futuro PostgreSQL:
    # SELECT name FROM categories WHERE slug = slug;
    item = next((cat for cat in CATEGORIES if cat["slug"] == slug), None)
    return item["name"] if item else "Especialistas"


@app.route("/")
def root():
    return redirect(url_for("splash", next="/login"))


@app.route("/inicio")
def splash():
    # Tela laranja de carregamento usada antes do login e depois do login.
    # O parâmetro next define para qual tela o usuário será enviado.
    next_url = request.args.get("next", "/login")
    return render_template("splash.html", next_url=next_url)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Futuro backend:
        # 1. Validar email/senha na tabela users.
        # 2. Criar sessão/JWT.
        # 3. Redirecionar para home se estiver correto.
        #
        # Exemplo:
        # user = auth_service.login(email, password)

        return redirect(url_for("splash", next="/home"))

    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        account_type = request.form.get("account_type")

        # Futuro backend:
        # INSERT INTO users (name, email, password_hash, account_type)
        # VALUES (...);
        #
        # Importante: nunca salvar senha pura no banco.
        # Usar hash de senha, por exemplo werkzeug.security.generate_password_hash.

        return redirect(url_for("splash", next="/home"))

    return render_template("cadastro.html")


@app.route("/home")
def home():
    # Futuro PostgreSQL:
    # Buscar categorias e especialistas online:
    # SELECT * FROM categories ORDER BY name;
    # SELECT * FROM specialists WHERE is_online = true LIMIT 3;
    online = SPECIALISTS[:3]
    return render_template("home.html", categories=CATEGORIES, specialists=online)


@app.route("/personalizacao")
def personalizacao():
    # Futuro backend:
    # Esta tela pode salvar nome da plataforma, logo e cor principal em tabela settings.
    #
    # Exemplo:
    # SELECT * FROM platform_settings LIMIT 1;
    # UPDATE platform_settings SET name = ..., primary_color = ...;
    return render_template("personalizacao.html")


@app.route("/especialistas")
def especialistas():
    category = request.args.get("categoria")
    filtered = SPECIALISTS
    title = "Especialistas disponíveis"
    subtitle = "14 profissionais online"

    if category:
        # Futuro PostgreSQL:
        # SELECT * FROM specialists WHERE category_slug = category AND is_online = true;
        filtered = [item for item in SPECIALISTS if item["category"] == category]
        title = f"Especialistas em {category_name(category)}"
        subtitle = f"{len(filtered)} profissional online" if len(filtered) == 1 else f"{len(filtered)} profissionais online"

    return render_template("especialistas.html", specialists=filtered, title=title, subtitle=subtitle)


@app.route("/especialista/<int:specialist_id>")
def especialista(specialist_id):
    # Futuro PostgreSQL:
    # Buscar especialista, especialidades e avaliações relacionadas.
    specialist = get_specialist(specialist_id)
    return render_template("perfil.html", specialist=specialist)


@app.route("/chamada/<int:specialist_id>")
def chamada(specialist_id):
    specialist = get_specialist(specialist_id)

    # Futuro PostgreSQL:
    # Ao iniciar chamada:
    # INSERT INTO calls (user_id, specialist_id, started_at, status)
    # VALUES (..., ..., NOW(), 'in_progress');
    #
    # Ao finalizar chamada:
    # UPDATE calls SET ended_at = NOW(), total_seconds = ..., total_value = ...
    # WHERE id = ...;

    return render_template("chamada.html", specialist=specialist)


@app.route("/pagamento/<int:specialist_id>")
def pagamento(specialist_id):
    specialist = get_specialist(specialist_id)

    # Futuro PostgreSQL:
    # SELECT call data FROM calls WHERE user_id = current_user AND specialist_id = specialist_id;
    # INSERT INTO payments (user_id, specialist_id, amount, method, status)
    # VALUES (..., ..., 1.25, 'credit_card', 'pending');

    return render_template("pagamento.html", specialist=specialist)


@app.route("/avaliacao/<int:specialist_id>", methods=["GET", "POST"])
def avaliacao(specialist_id):
    specialist = get_specialist(specialist_id)

    if request.method == "POST":
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        # Futuro PostgreSQL:
        # INSERT INTO reviews (user_id, specialist_id, rating, comment, created_at)
        # VALUES (..., specialist_id, rating, comment, NOW());

        return redirect(url_for("home"))

    return render_template("avaliacao.html", specialist=specialist)


if __name__ == "__main__":
    app.run(debug=True)
