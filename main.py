from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Controller.usuario_controller import router as usuario_router
from Controller.especialista_controller import router as especialista_router
from Controller.ia_controller import router as ia_router


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
            "request": request
        }
    )


@app.get("/cadastro", name="auth.cadastro")
def cadastro(request: Request):
    return templates.TemplateResponse(
        "cadastro.html",
        {
            "request": request
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
