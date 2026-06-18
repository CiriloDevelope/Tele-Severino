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


def get_specialist(specialist_id: int):
    return next(
        (item for item in specialists if item["id"] == specialist_id),
        specialists[0]
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

        return RedirectResponse(
            f"/especialista/dashboard?usuario_id={id_usuario}",
            status_code=303
        )

    return RedirectResponse(
        f"/home?usuario_id={id_usuario}",
        status_code=303
    )


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
        return RedirectResponse(
            f"/especialista/dashboard?usuario_id={id_usuario}",
            status_code=303
        )

    return RedirectResponse(
        f"/home?usuario_id={id_usuario}",
        status_code=303
    )


@app.get("/especialista/dashboard", name="specialist.dashboard")
def especialista_dashboard(request: Request, usuario_id: int = 0):
    return templates.TemplateResponse(
        "especialista_dashboard.html",
        {
            "request": request,
            "usuario_id": usuario_id
        }
    )


@app.get("/logout", name="auth.logout")
def logout():
    return RedirectResponse("/login")


@app.get("/home", name="home")
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "categories": categories,
            "specialists": specialists
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
            "specialists": specialists
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
