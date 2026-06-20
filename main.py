from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Controller.usuario_controller import router as usuario_router
from Controller.especialista_controller import router as especialista_router
from Controller.ia_controller import router as ia_router
from Model.database import conectar_banco
from Model.usuario_model import senha_hash, consultar_usuarios


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Tele Severino")

# Arquivos estáticos: CSS e JavaScript
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "View" / "static")),
    name="static"
)

# Templates HTML
templates = Jinja2Templates(directory=str(BASE_DIR / "View" / "templates"))


# Rotas da API
app.include_router(usuario_router)
app.include_router(especialista_router)
app.include_router(ia_router)


# Dados simulados para o frontend
categories = [
    {
        "name": "Casa e Reparos",
        "slug": "casa",
        "icon": "🏠",
        "tone": "orange"
    },
    {
        "name": "Tecnologia",
        "slug": "tecnologia",
        "icon": "💻",
        "tone": "blue"
    },
    {
        "name": "Culinária",
        "slug": "culinaria",
        "icon": "🍳",
        "tone": "green"
    },
    {
        "name": "Estudos",
        "slug": "estudos",
        "icon": "📚",
        "tone": "purple"
    }
]


specialists = [
    {
        "id": 1,
        "name": "Bete Oliveira",
        "initials": "BO",
        "role": "Consultora doméstica",
        "price": "2,50",
        "rating": "4.9",
        "reviews": 128,
        "avatar_class": "avatar-orange",
        "about": "Ajuda com organização residencial, rotina doméstica e pequenas dúvidas do dia a dia.",
        "tags": ["Organização", "Casa", "Atendimento rápido"]
    },
    {
        "id": 2,
        "name": "Carlos Silva",
        "initials": "CS",
        "role": "Técnico de informática",
        "price": "3,00",
        "rating": "4.8",
        "reviews": 97,
        "avatar_class": "avatar-blue",
        "about": "Suporte rápido para computador, celular, internet e configurações básicas.",
        "tags": ["Informática", "Celular", "Internet"]
    },
    {
        "id": 3,
        "name": "Ana Souza",
        "initials": "AS",
        "role": "Mentora de estudos",
        "price": "2,00",
        "rating": "5.0",
        "reviews": 75,
        "avatar_class": "avatar-purple",
        "about": "Ajuda estudantes a organizarem tarefas, trabalhos e rotina de estudos.",
        "tags": ["Estudos", "Organização", "Faculdade"]
    }
]


def format_price(value):
    try:
        return f"{float(value):.2f}".replace(".", ",")
    except Exception:
        return "0,00"


def get_db_specialists():
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        sql = """
        SELECT
            u.id_usuario,
            u.nome,
            e.especialidade,
            e.valor_minuto
        FROM especialistas e
        INNER JOIN usuarios u
            ON u.id_usuario = e.id_especialista
        WHERE u.tipo = 'ESPECIALISTA'
        ORDER BY u.id_usuario DESC
        """

        cursor.execute(sql)
        rows = cursor.fetchall()

        db_specialists = []

        for row in rows:
            nome = row["nome"]
            initials = "".join([parte[0] for parte in nome.split()[:2]]).upper()

            db_specialists.append({
                "id": row["id_usuario"],
                "name": nome,
                "initials": initials,
                "role": row["especialidade"],
                "price": format_price(row["valor_minuto"]),
                "rating": "5.0",
                "reviews": 0,
                "avatar_class": "avatar-orange",
                "about": f"{nome} atende na área de {row['especialidade']} pelo Tele Severino.",
                "tags": [row["especialidade"], "Atendimento online", "Consultoria por minuto"]
            })

        return db_specialists

    except Exception as erro:
        print(f"Erro ao buscar especialistas do banco: {erro}")
        return specialists

    finally:
        if conexao:
            conexao.close()


def get_specialist(specialist_id: int):
    db_specialists = get_db_specialists()

    return next(
        (item for item in db_specialists if item["id"] == specialist_id),
        db_specialists[0] if db_specialists else specialists[0]
    )


def cadastrar_usuario_frontend(nome: str, email: str, senha: str, tipo: str):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (%s, %s, %s, %s)
        """

        valores = (nome, email, senha_hash(senha), tipo)
        cursor.execute(sql, valores)
        conexao.commit()

        return {
            "sucesso": True,
            "id_usuario": cursor.lastrowid
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": str(erro)
        }

    finally:
        if conexao:
            conexao.close()


def cadastrar_especialista_frontend(id_usuario: int, especialidade: str, valor_minuto: float):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO especialistas (id_especialista, especialidade, valor_minuto)
        VALUES (%s, %s, %s)
        """

        valores = (id_usuario, especialidade, valor_minuto)
        cursor.execute(sql, valores)
        conexao.commit()

        return {
            "sucesso": True
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": str(erro)
        }

    finally:
        if conexao:
            conexao.close()


def usuario_logado(request: Request):
    usuario_id = request.cookies.get("usuario_id")
    usuario_tipo = request.cookies.get("usuario_tipo")

    if not usuario_id or not usuario_tipo:
        return None

    return {
        "id": usuario_id,
        "tipo": usuario_tipo
    }


def exigir_login(request: Request):
    usuario = usuario_logado(request)

    if not usuario:
        return RedirectResponse("/login", status_code=303)

    return usuario


@app.get("/", name="splash")
def splash(request: Request):
    return templates.TemplateResponse(
        "splash.html",
        {
            "request": request,
            "next_url": "/login"
        }
    )


@app.get("/login", name="auth.login")
def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "erro": None
        }
    )


@app.get("/cadastro", name="auth.cadastro")
def cadastro(request: Request):
    return templates.TemplateResponse(
        "cadastro.html",
        {
            "request": request,
            "erro": None
        }
    )


@app.post("/cadastro")
def cadastro_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    account_type: str = Form(...),
    especialidade: str = Form(""),
    valor_minuto: str = Form("0")
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "cadastro.html",
            {
                "request": request,
                "erro": "As senhas não conferem."
            }
        )

    tipo = "ESPECIALISTA" if account_type == "specialist" else "CLIENTE"

    if tipo == "ESPECIALISTA":
        if not especialidade.strip():
            return templates.TemplateResponse(
                "cadastro.html",
                {
                    "request": request,
                    "erro": "Informe a especialidade do especialista."
                }
            )

        try:
            valor_float = float(valor_minuto.replace(",", "."))
        except ValueError:
            return templates.TemplateResponse(
                "cadastro.html",
                {
                    "request": request,
                    "erro": "Informe um valor por minuto válido."
                }
            )
    else:
        valor_float = 0

    resultado_usuario = cadastrar_usuario_frontend(name, email, password, tipo)

    if not resultado_usuario["sucesso"]:
        return templates.TemplateResponse(
            "cadastro.html",
            {
                "request": request,
                "erro": f"Não foi possível cadastrar: {resultado_usuario['erro']}"
            }
        )

    id_usuario = resultado_usuario["id_usuario"]

    if tipo == "ESPECIALISTA":
        resultado_especialista = cadastrar_especialista_frontend(
            id_usuario,
            especialidade,
            valor_float
        )

        if not resultado_especialista["sucesso"]:
            return templates.TemplateResponse(
                "cadastro.html",
                {
                    "request": request,
                    "erro": f"Usuário criado, mas houve erro ao cadastrar especialista: {resultado_especialista['erro']}"
                }
            )

        response = RedirectResponse(
            f"/especialista/dashboard?usuario_id={id_usuario}",
            status_code=303
        )
        response.set_cookie("usuario_id", str(id_usuario))
        response.set_cookie("usuario_tipo", "ESPECIALISTA")
        return response

    response = RedirectResponse(
        f"/home?usuario_id={id_usuario}",
        status_code=303
    )
    response.set_cookie("usuario_id", str(id_usuario))
    response.set_cookie("usuario_tipo", "CLIENTE")
    return response


@app.post("/login-web")
def login_web(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    usuario = consultar_usuarios(email)

    if usuario is None or isinstance(usuario, dict):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "erro": "Usuário não encontrado."
            }
        )

    id_usuario = usuario[0]
    senha_banco = usuario[3]
    tipo_usuario = usuario[4]

    if senha_banco != senha_hash(password):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "erro": "E-mail ou senha inválidos."
            }
        )

    if tipo_usuario == "ESPECIALISTA":
        response = RedirectResponse(
            f"/especialista/dashboard?usuario_id={id_usuario}",
            status_code=303
        )
        response.set_cookie("usuario_id", str(id_usuario))
        response.set_cookie("usuario_tipo", "ESPECIALISTA")
        return response

    response = RedirectResponse(
        f"/home?usuario_id={id_usuario}",
        status_code=303
    )
    response.set_cookie("usuario_id", str(id_usuario))
    response.set_cookie("usuario_tipo", "CLIENTE")
    return response


@app.get("/especialista/dashboard", name="specialist.dashboard")
def especialista_dashboard(request: Request, usuario_id: int = 0):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "ESPECIALISTA":
        return RedirectResponse("/home", status_code=303)

    return templates.TemplateResponse(
        "especialista_dashboard.html",
        {
            "request": request,
            "usuario_id": usuario["id"]
        }
    )


@app.get("/logout", name="auth.logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("usuario_id")
    response.delete_cookie("usuario_tipo")
    return response


@app.get("/home", name="home")
def home(request: Request):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] == "ESPECIALISTA":
        return RedirectResponse(
            f"/especialista/dashboard?usuario_id={usuario['id']}",
            status_code=303
        )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "categories": categories,
            "specialists": get_db_specialists()
        }
    )


@app.get("/especialistas", name="specialist.especialistas")
def especialistas_page(request: Request):
    return templates.TemplateResponse(
        "especialistas.html",
        {
            "request": request,
            "title": "Especialistas",
            "subtitle": "Escolha um profissional disponível",
            "specialists": get_db_specialists()
        }
    )


@app.get("/perfil/{specialist_id}", name="specialist.especialista")
def perfil(request: Request, specialist_id: int):
    return templates.TemplateResponse(
        "perfil.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.get("/chamada/{specialist_id}", name="call.chamada")
def chamada(request: Request, specialist_id: int):
    return templates.TemplateResponse(
        "chamada.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.get("/pagamento/{specialist_id}", name="payment.pagamento")
def pagamento(request: Request, specialist_id: int):
    return templates.TemplateResponse(
        "pagamento.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.get("/avaliacao/{specialist_id}", name="review.avaliacao")
def avaliacao(request: Request, specialist_id: int):
    return templates.TemplateResponse(
        "avaliacao.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.post("/avaliacao/{specialist_id}")
def enviar_avaliacao(specialist_id: int):
    return RedirectResponse("/home", status_code=303)


@app.get("/personalizacao", name="brand.personalizacao")
def personalizacao(request: Request):
    return templates.TemplateResponse(
        "personalizacao.html",
        {
            "request": request
        }
    )
