import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Form, UploadFile, File
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



def normalizar_texto_categoria(valor):
    import unicodedata

    texto = str(valor or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(char for char in texto if not unicodedata.combining(char))

    for antigo, novo in {
        " ": "-",
        "_": "-",
        "/": "-",
        "\\": "-",
        ",": "-",
        ".": "",
    }.items():
        texto = texto.replace(antigo, novo)

    while "--" in texto:
        texto = texto.replace("--", "-")

    return texto.strip("-")


def separar_tags(tags, especialidade):
    if tags:
        return [tag.strip() for tag in str(tags).split(",") if tag.strip()]

    return [especialidade, "Atendimento online", "Consultoria por minuto"]


def identificar_categoria_especialista(row):
    categoria_original = normalizar_texto_categoria(row.get("categoria"))

    categorias_conhecidas = {
        "casa": "casa",
        "casa-e-reparos": "casa",
        "tecnologia": "tecnologia",
        "culinaria": "culinaria",
        "estudos": "estudos",
    }

    if categoria_original in categorias_conhecidas:
        return categorias_conhecidas[categoria_original]

    especialidade = normalizar_texto_categoria(row.get("especialidade"))
    descricao = normalizar_texto_categoria(row.get("descricao"))
    tags = normalizar_texto_categoria(row.get("tags"))

    texto_geral = f"{categoria_original} {especialidade} {descricao} {tags}"

    if any(termo in texto_geral for termo in [
        "culinaria", "cozinha", "receita", "bolo", "comida", "gastronomia"
    ]):
        return "culinaria"

    if any(termo in texto_geral for termo in [
        "estudos", "faculdade", "escola", "aula", "mentoria", "trabalho",
        "prova", "academico", "organizacao-de-estudos"
    ]):
        return "estudos"

    if any(termo in texto_geral for termo in [
        "tecnologia", "informatica", "computador", "celular", "internet",
        "software", "programacao", "front-end", "frontend", "back-end",
        "backend", "sistema", "automacao", "automatizacao"
    ]):
        return "tecnologia"

    if any(termo in texto_geral for termo in [
        "eletrica", "eletricista", "tomada", "chuveiro", "disjuntor",
        "casa", "reparo", "reparos", "manutencao", "residencial",
        "domestica", "consultoria-domestica"
    ]):
        return "casa"

    return "casa"


def obter_nome_categoria(slug):
    for categoria in categories:
        if categoria["slug"] == slug:
            return categoria["name"]

    nomes = {
        "casa": "Casa e Reparos",
        "tecnologia": "Tecnologia",
        "culinaria": "Culinária",
        "estudos": "Estudos",
    }

    return nomes.get(slug, "Especialistas")


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
            e.valor_minuto,
            e.foto_perfil,
            e.categoria,
            e.descricao,
            e.tempo_medio,
            e.indicacao,
            e.tags
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

            categoria_slug = identificar_categoria_especialista(row)
            descricao = row.get("descricao") or f"{nome} atende na área de {row['especialidade']} pelo Tele Severino."

            db_specialists.append({
                "id": row["id_usuario"],
                "name": nome,
                "initials": initials,
                "role": row["especialidade"],
                "price": format_price(row["valor_minuto"]),
                "rating": "0.0",
                "reviews": 0,
                "avatar_class": "avatar-orange",
                "foto_perfil": row.get("foto_perfil"),
                "about": descricao,
                "category": row.get("categoria") or obter_nome_categoria(categoria_slug),
                "category_slug": categoria_slug,
                "tags": separar_tags(row.get("tags"), row["especialidade"])
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


def consultar_cadastro_complementar(id_usuario: int):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        sql = """
        SELECT *
        FROM cadastros_complementares
        WHERE id_usuario = %s
        """

        cursor.execute(sql, (id_usuario,))
        return cursor.fetchone()

    except Exception as erro:
        print(f"Erro ao consultar cadastro complementar: {erro}")
        return None

    finally:
        if conexao:
            conexao.close()


def salvar_cadastro_complementar(
    id_usuario: int,
    tipo_usuario: str,
    cpf_cnpj: str,
    telefone: str = "",
    forma_pagamento: str = "",
    apelido_pagamento: str = "",
    chave_pix: str = "",
    banco: str = "",
    tipo_conta: str = ""
):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cadastro_existente = consultar_cadastro_complementar(id_usuario)

        if cadastro_existente:
            sql = """
            UPDATE cadastros_complementares
            SET
                telefone = %s,
                forma_pagamento = %s,
                apelido_pagamento = %s,
                chave_pix = %s,
                banco = %s,
                tipo_conta = %s
            WHERE id_usuario = %s
            """

            valores = (
                telefone,
                forma_pagamento,
                apelido_pagamento,
                chave_pix,
                banco,
                tipo_conta,
                id_usuario
            )

            cursor.execute(sql, valores)
            conexao.commit()

            return {
                "sucesso": True,
                "mensagem": "Cadastro complementar atualizado com sucesso. CPF/CNPJ mantido sem alteração."
            }

        sql = """
        INSERT INTO cadastros_complementares (
            id_usuario,
            tipo_usuario,
            cpf_cnpj,
            telefone,
            forma_pagamento,
            apelido_pagamento,
            chave_pix,
            banco,
            tipo_conta
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            id_usuario,
            tipo_usuario,
            cpf_cnpj,
            telefone,
            forma_pagamento,
            apelido_pagamento,
            chave_pix,
            banco,
            tipo_conta
        )

        cursor.execute(sql, valores)
        conexao.commit()

        return {
            "sucesso": True,
            "mensagem": "Cadastro complementar salvo com sucesso."
        }

    except Exception as erro:
        return {
            "sucesso": False,
            "erro": str(erro)
        }

    finally:
        if conexao:
            conexao.close()



def exigir_cliente(request: Request):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "CLIENTE":
        return RedirectResponse(
            f"/especialista/dashboard?usuario_id={usuario['id']}",
            status_code=303
        )

    return usuario


def exigir_especialista(request: Request):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "ESPECIALISTA":
        return RedirectResponse("/home", status_code=303)

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
    usuario = exigir_especialista(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "ESPECIALISTA":
        return RedirectResponse("/home", status_code=303)

    return templates.TemplateResponse(
        "especialista_resumo.html",
        {
            "request": request,
            "usuario_id": usuario["id"],
            "cadastro_complementar": consultar_cadastro_complementar(int(usuario["id"])),
            "especialista": consultar_especialista_por_usuario(int(usuario["id"])),
            "active_page": "resumo"
        }
    )


@app.post("/cadastro-complementar")
def cadastro_complementar_post(
    request: Request,
    cpf_cnpj: str = Form(...),
    telefone: str = Form(""),
    forma_pagamento: str = Form(""),
    apelido_pagamento: str = Form(""),
    chave_pix: str = Form(""),
    banco: str = Form(""),
    tipo_conta: str = Form("")
):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    id_usuario = int(usuario["id"])
    tipo_usuario = usuario["tipo"]

    resultado = salvar_cadastro_complementar(
        id_usuario=id_usuario,
        tipo_usuario=tipo_usuario,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        forma_pagamento=forma_pagamento,
        apelido_pagamento=apelido_pagamento,
        chave_pix=chave_pix,
        banco=banco,
        tipo_conta=tipo_conta
    )

    if not resultado["sucesso"]:
        print(f"Erro ao salvar cadastro complementar: {resultado['erro']}")

    if tipo_usuario == "ESPECIALISTA":
        return RedirectResponse(
            f"/especialista/dashboard?usuario_id={id_usuario}",
            status_code=303
        )

    return RedirectResponse(
        f"/home?usuario_id={id_usuario}",
        status_code=303
    )


@app.get("/logout", name="auth.logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("usuario_id")
    response.delete_cookie("usuario_tipo")
    return response


@app.get("/home", name="home")
def home(request: Request):
    usuario = exigir_cliente(request)

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
            "specialists": get_db_specialists(),
            "cadastro_complementar": consultar_cadastro_complementar(int(usuario["id"]))
        }
    )


@app.get("/especialistas", name="specialist.especialistas")
def especialistas_page(request: Request, categoria: str = ""):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    todos_especialistas = get_db_specialists()
    categoria_selecionada = normalizar_texto_categoria(categoria)

    if categoria_selecionada:
        specialists_filtrados = [
            specialist for specialist in todos_especialistas
            if specialist.get("category_slug") == categoria_selecionada
        ]

        nome_categoria = obter_nome_categoria(categoria_selecionada)
        title = nome_categoria
        subtitle = f"Especialistas disponíveis em {nome_categoria}"
    else:
        specialists_filtrados = todos_especialistas
        title = "Especialistas"
        subtitle = "Escolha um profissional disponível"

    return templates.TemplateResponse(
        "especialistas.html",
        {
            "request": request,
            "title": title,
            "subtitle": subtitle,
            "specialists": specialists_filtrados,
            "categories": categories,
            "categoria_selecionada": categoria_selecionada
        }
    )


@app.get("/perfil/{specialist_id}", name="specialist.especialista")
def perfil(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates.TemplateResponse(
        "perfil.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.get("/chamada/{specialist_id}", name="call.chamada")
def chamada(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates.TemplateResponse(
        "chamada.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.get("/pagamento/{specialist_id}", name="payment.pagamento")
def pagamento(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates.TemplateResponse(
        "pagamento.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.get("/avaliacao/{specialist_id}", name="review.avaliacao")
def avaliacao(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates.TemplateResponse(
        "avaliacao.html",
        {
            "request": request,
            "specialist": get_specialist(specialist_id)
        }
    )


@app.post("/avaliacao/{specialist_id}")
def enviar_avaliacao(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    return RedirectResponse("/home", status_code=303)


@app.get("/personalizacao", name="brand.personalizacao")
def personalizacao(request: Request):
    return templates.TemplateResponse(
        "personalizacao.html",
        {
            "request": request
        }
    )

@app.get("/especialista/assinatura")
def especialista_assinatura(request: Request):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "ESPECIALISTA":
        return RedirectResponse("/home", status_code=303)

    return templates.TemplateResponse(
        "especialista_assinatura.html",
        {
            "request": request,
            "usuario_id": usuario["id"],
            "cadastro_complementar": consultar_cadastro_complementar(int(usuario["id"])),
            "especialista": consultar_especialista_por_usuario(int(usuario["id"])),
            "active_page": "assinatura"
        }
    )

def render_especialista_page(request: Request, template_name: str, active_page: str):
    usuario = exigir_especialista(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "ESPECIALISTA":
        return RedirectResponse("/home", status_code=303)

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "usuario_id": usuario["id"],
            "cadastro_complementar": consultar_cadastro_complementar(int(usuario["id"])),
            "especialista": consultar_especialista_por_usuario(int(usuario["id"])),
            "active_page": active_page
        }
    )


@app.get("/especialista/cupons")
def especialista_cupons(request: Request):
    return render_especialista_page(request, "especialista_cupons.html", "cupons")


@app.get("/especialista/perfil")
def especialista_perfil(request: Request):
    return render_especialista_page(request, "especialista_perfil.html", "perfil")


@app.get("/especialista/ganhos")
def especialista_ganhos(request: Request):
    return render_especialista_page(request, "especialista_ganhos.html", "ganhos")


@app.get("/especialista/agenda")
def especialista_agenda(request: Request):
    return render_especialista_page(request, "especialista_agenda.html", "agenda")


@app.get("/especialista/notificacoes")
def especialista_notificacoes(request: Request):
    return render_especialista_page(request, "especialista_notificacoes.html", "notificacoes")


@app.get("/especialista/mensagens")
def especialista_mensagens(request: Request):
    return render_especialista_page(request, "especialista_mensagens.html", "mensagens")


@app.get("/especialista/recebimento")
def especialista_recebimento(request: Request):
    return render_especialista_page(request, "especialista_recebimento.html", "recebimento")

def consultar_especialista_por_usuario(id_usuario: int):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        sql = """
        SELECT
            e.id_especialista,
            e.especialidade,
            e.valor_minuto,
            e.foto_perfil,
            e.categoria,
            e.descricao,
            e.tempo_medio,
            e.indicacao,
            e.tags,
            u.nome
        FROM especialistas e
        INNER JOIN usuarios u
            ON u.id_usuario = e.id_especialista
        WHERE e.id_especialista = %s
        """

        cursor.execute(sql, (id_usuario,))
        return cursor.fetchone()

    except Exception as erro:
        print(f"Erro ao consultar especialista: {erro}")
        return None

    finally:
        if conexao:
            conexao.close()


def salvar_foto_perfil_especialista(id_usuario: int, foto_perfil: str):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        UPDATE especialistas
        SET foto_perfil = %s
        WHERE id_especialista = %s
        """

        cursor.execute(sql, (foto_perfil, id_usuario))
        conexao.commit()
        return True

    except Exception as erro:
        print(f"Erro ao salvar foto do especialista: {erro}")
        return False

    finally:
        if conexao:
            conexao.close()


@app.post("/especialista/perfil/foto")
async def especialista_upload_foto(request: Request, foto_perfil: UploadFile = File(...)):
    usuario = exigir_especialista(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "ESPECIALISTA":
        return RedirectResponse("/home", status_code=303)

    extensoes_permitidas = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }

    if foto_perfil.content_type not in extensoes_permitidas:
        return RedirectResponse("/especialista/perfil?erro=tipo_arquivo", status_code=303)

    extensao = extensoes_permitidas[foto_perfil.content_type]
    nome_arquivo = f"especialista_{usuario['id']}_{uuid.uuid4().hex}{extensao}"

    pasta_upload = Path("View/static/uploads/perfis")
    pasta_upload.mkdir(parents=True, exist_ok=True)

    caminho_arquivo = pasta_upload / nome_arquivo

    conteudo = await foto_perfil.read()

    limite_mb = 8 * 1024 * 1024
    if len(conteudo) > limite_mb:
        return RedirectResponse("/especialista/perfil?erro=tamanho_arquivo", status_code=303)

    caminho_arquivo.write_bytes(conteudo)

    caminho_publico = f"/static/uploads/perfis/{nome_arquivo}"
    salvar_foto_perfil_especialista(int(usuario["id"]), caminho_publico)

    return RedirectResponse("/especialista/perfil", status_code=303)

@app.post("/especialista/perfil/dados")
def especialista_salvar_perfil_dados(
    request: Request,
    nome: str = Form(...),
    categoria: str = Form(""),
    especialidade: str = Form(...),
    descricao: str = Form(""),
    tempo_medio: str = Form(""),
    indicacao: str = Form(""),
    tags: str = Form(""),
    valor_minuto: str = Form(...)
):
    usuario = exigir_especialista(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "ESPECIALISTA":
        return RedirectResponse("/home", status_code=303)

    valor_minuto_normalizado = str(valor_minuto).replace(",", ".")

    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql_usuario = """
        UPDATE usuarios
        SET nome = %s
        WHERE id_usuario = %s
        """

        cursor.execute(sql_usuario, (nome, usuario["id"]))

        sql_especialista = """
        UPDATE especialistas
        SET categoria = %s,
            especialidade = %s,
            descricao = %s,
            tempo_medio = %s,
            indicacao = %s,
            tags = %s,
            valor_minuto = %s
        WHERE id_especialista = %s
        """

        cursor.execute(
            sql_especialista,
            (
                categoria,
                especialidade,
                descricao,
                tempo_medio,
                indicacao,
                tags,
                valor_minuto_normalizado,
                usuario["id"]
            )
        )

        conexao.commit()

    except Exception as erro:
        print(f"Erro ao salvar perfil do especialista: {erro}")

    finally:
        if conexao:
            conexao.close()

    return RedirectResponse("/especialista/perfil", status_code=303)
@app.get("/especialista/financeiro")
def especialista_financeiro(request: Request):
    return render_especialista_page(request, "especialista_financeiro.html", "financeiro")


@app.get("/especialista/operacao")
def especialista_operacao(request: Request):
    return render_especialista_page(request, "especialista_operacao.html", "operacao")


@app.get("/favicon.ico", include_in_schema=False)
def favicon_ico():
    return RedirectResponse(url="/static/favicon.svg")

