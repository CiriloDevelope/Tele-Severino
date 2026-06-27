import os
from datetime import date
import calendar
import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse
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
        "rating": "0.0",
        "reviews": 0,
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
        "rating": "0.0",
        "reviews": 0,
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
        "rating": "0.0",
        "reviews": 0,
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





def garantir_tabela_avaliacoes():
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id_avaliacao INT AUTO_INCREMENT PRIMARY KEY,
                id_consultoria INT NULL,
                id_cliente INT NULL,
                id_especialista INT NULL,
                nota INT NULL,
                comentario TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("SHOW COLUMNS FROM avaliacoes")
        colunas = {row["Field"] for row in cursor.fetchall()}

        if "id_cliente" not in colunas:
            cursor.execute("ALTER TABLE avaliacoes ADD COLUMN id_cliente INT NULL DEFAULT NULL")

        if "id_especialista" not in colunas:
            cursor.execute("ALTER TABLE avaliacoes ADD COLUMN id_especialista INT NULL DEFAULT NULL")

        if "data_criacao" not in colunas:
            cursor.execute("ALTER TABLE avaliacoes ADD COLUMN data_criacao TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP")

        if "id_consultoria" in colunas:
            cursor.execute("ALTER TABLE avaliacoes MODIFY COLUMN id_consultoria INT NULL DEFAULT NULL")

        conexao.commit()
    finally:
        if conexao:
            conexao.close()


def consultar_resumo_avaliacoes(id_especialista):
    garantir_tabela_avaliacoes()

    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                COUNT(*) AS total,
                COALESCE(AVG(nota), 0) AS media
            FROM avaliacoes
            WHERE id_especialista = %s
            """,
            (id_especialista,)
        )

        row = cursor.fetchone() or {"total": 0, "media": 0}

        return {
            "rating": f"{float(row['media']):.1f}",
            "reviews": int(row["total"] or 0)
        }

    finally:
        if conexao:
            conexao.close()


def consultar_avaliacoes_especialista(id_especialista, limite=5):
    garantir_tabela_avaliacoes()

    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                a.nota,
                a.comentario,
                DATE_FORMAT(a.data_criacao, '%d/%m/%Y') AS data,
                COALESCE(u.nome, 'Cliente') AS cliente
            FROM avaliacoes a
            LEFT JOIN usuarios u
                ON u.id_usuario = a.id_cliente
            WHERE a.id_especialista = %s
            ORDER BY a.data_criacao DESC
            LIMIT %s
            """,
            (id_especialista, limite)
        )

        rows = cursor.fetchall()

        return [
            {
                "nota": int(row["nota"]),
                "comentario": row.get("comentario") or "",
                "data": row.get("data") or "",
                "cliente": row.get("cliente") or "Cliente",
                "estrelas": "★" * int(row["nota"])
            }
            for row in rows
        ]

    finally:
        if conexao:
            conexao.close()


def salvar_avaliacao_especialista(id_cliente, id_especialista, nota, comentario):
    garantir_tabela_avaliacoes()

    conexao = None
    try:
        nota = int(nota)
        nota = max(1, min(nota, 5))

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            """
            INSERT INTO avaliacoes (
                id_cliente,
                id_especialista,
                nota,
                comentario
            )
            VALUES (%s, %s, %s, %s)
            """,
            (id_cliente, id_especialista, nota, comentario)
        )

        conexao.commit()
        return True

    except Exception as erro:
        print(f"Erro ao salvar avaliação: {erro}")
        return False

    finally:
        if conexao:
            conexao.close()



def obter_plano_label(plano):
    plano = str(plano or "FREE").upper()

    if plano == "PROFISSIONAL":
        return "Profissional"

    if plano == "PLUS":
        return "Plus"

    return "Free"


def obter_status_label(status):
    status = str(status or "ONLINE").upper()

    if status == "OFFLINE":
        return {
            "status": "OFFLINE",
            "label": "Offline",
            "is_online": False
        }

    return {
        "status": "ONLINE",
        "label": "Online agora",
        "is_online": True
    }


def montar_agenda_disponibilidade(plano):
    plano = str(plano or "FREE").upper()
    hoje = date.today()
    total_dias = calendar.monthrange(hoje.year, hoje.month)[1]

    nomes_semana = {
        0: "Seg",
        1: "Ter",
        2: "Qua",
        3: "Qui",
        4: "Sex",
        5: "Sáb",
        6: "Dom"
    }

    meses = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    dias = []

    for numero_dia in range(1, total_dias + 1):
        data_dia = date(hoje.year, hoje.month, numero_dia)
        semana = data_dia.weekday()
        fim_de_semana = semana >= 5
        passado = data_dia < hoje

        slots = []
        bloqueado = ""

        if passado:
            bloqueado = "Data passada"
        elif plano == "FREE":
            if fim_de_semana:
                bloqueado = "Finais de semana não liberados no plano Free"
            else:
                slots = ["18:30", "19:30", "20:30"]
        elif plano == "PROFISSIONAL":
            if semana == 6:
                bloqueado = "Domingo disponível apenas no plano Plus"
            elif semana == 5:
                slots = ["09:00", "11:00"]
            else:
                slots = ["09:00", "10:30", "14:00", "18:30", "20:00"]
        elif plano == "PLUS":
            if fim_de_semana:
                slots = ["09:00", "11:00", "15:00"]
            else:
                slots = ["08:00", "10:00", "14:00", "18:30", "20:30"]

        dias.append({
            "dia": numero_dia,
            "semana": nomes_semana[semana],
            "is_today": data_dia == hoje,
            "is_available": bool(slots),
            "slots": slots,
            "slots_text": ",".join(slots),
            "bloqueado": bloqueado
        })

    regras = {
        "FREE": "segunda a sexta, somente pós-comercial. Sábado e domingo bloqueados.",
        "PROFISSIONAL": "segunda a sexta com horário comercial e pós-comercial. Sábado limitado. Domingo bloqueado.",
        "PLUS": "agenda liberada de segunda a domingo, com mais horários disponíveis."
    }

    return {
        "plano": plano,
        "plano_label": obter_plano_label(plano),
        "mes_label": f"{meses[hoje.month]} {hoje.year}",
        "regras": regras.get(plano, regras["FREE"]),
        "dias": dias
    }


def payment_cookie_name(usuario_id, specialist_id):
    return f"pagamento_aprovado_{usuario_id}_{specialist_id}"


def get_fake_payment_profile(usuario):
    cadastro = consultar_cadastro_complementar(int(usuario["id"]))

    return {
        "has_saved_card": True,
        "card_brand": "Visa",
        "card_last4": "4532",
        "card_holder": "Cliente Tele Severino",
        "pix_key": "pagamento@teleseverino.local",
        "pix_code": f"00020126580014br.gov.bcb.pix0136tele-severino-{usuario['id']}5204000053039865802BR5925TELE SEVERINO PROTOTIPO6009SAO PAULO62070503***6304FAKE"
    }


def format_duration(seconds):
    try:
        seconds = int(seconds)
    except Exception:
        seconds = 15

    seconds = max(1, min(seconds, 14400))

    horas = seconds // 3600
    minutos = (seconds % 3600) // 60
    segundos = seconds % 60

    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


def get_price_value(specialist):
    valor = specialist.get("price_value")

    if valor is not None:
        try:
            return float(valor)
        except Exception:
            pass

    texto = str(specialist.get("price", "0")).replace("R$", "").strip()
    texto = texto.replace(",", ".")

    try:
        return float(texto)
    except Exception:
        return 0.0


def montar_resumo_pagamento(specialist, tempo):
    try:
        segundos = int(tempo)
    except Exception:
        segundos = 15

    segundos = max(1, min(segundos, 14400))

    valor_minuto = get_price_value(specialist)
    total = (segundos / 60) * valor_minuto

    if total <= 0:
        total = 0.01

    return {
        "duration_seconds": segundos,
        "duration": format_duration(segundos),
        "price_per_minute": format_price(valor_minuto),
        "total": format_price(total),
        "total_value": round(total, 2)
    }



SEVERINO_RESPOSTAS_PADRAO = [
    {
        "intencao": "casa_reparos",
        "gatilhos": "chuveiro, tomada, eletrica, elétrica, disjuntor, lampada, lâmpada, encanamento, torneira, vazamento, parede, porta, reparo",
        "resposta": "Entendi! Isso parece ser algo de Casa e Reparos. Posso te mostrar especialistas disponíveis para te ajudar agora.",
        "categoria_slug": "casa",
        "acao_label": "Ver Casa e Reparos",
        "acao_url": "/especialistas?categoria=casa"
    },
    {
        "intencao": "tecnologia",
        "gatilhos": "computador, notebook, celular, internet, wifi, wi-fi, aplicativo, app, sistema, tela, erro, impressora",
        "resposta": "Beleza! Isso parece ser um assunto de Tecnologia. Vou te indicar especialistas que podem ajudar com suporte técnico.",
        "categoria_slug": "tecnologia",
        "acao_label": "Ver Tecnologia",
        "acao_url": "/especialistas?categoria=tecnologia"
    },
    {
        "intencao": "culinaria",
        "gatilhos": "cozinha, receita, comida, bolo, churrasco, tempero, carne, almoço, jantar, culinaria, culinária",
        "resposta": "Legal! Isso combina com Culinária. Posso te mostrar especialistas para te orientar com receitas e preparo.",
        "categoria_slug": "culinaria",
        "acao_label": "Ver Culinária",
        "acao_url": "/especialistas?categoria=culinaria"
    },
    {
        "intencao": "estudos",
        "gatilhos": "faculdade, prova, trabalho, estudo, estudar, matematica, matemática, programação, aula, escola, tarefa",
        "resposta": "Entendi! Isso parece ser uma dúvida de Estudos. Posso te mostrar especialistas para te ajudar com esse assunto.",
        "categoria_slug": "estudos",
        "acao_label": "Ver Estudos",
        "acao_url": "/especialistas?categoria=estudos"
    },
    {
        "intencao": "preco",
        "gatilhos": "preço, preco, valor, custa, cobrar, barato, caro, minuto, pagamento",
        "resposta": "No Tele-Severino, cada especialista possui um valor por minuto. Você pode comparar os profissionais usando os filtros de mais barato e mais caro.",
        "categoria_slug": "",
        "acao_label": "Ver especialistas",
        "acao_url": "/especialistas"
    },
    {
        "intencao": "online",
        "gatilhos": "online, agora, disponivel, disponível, atender, atendimento, urgente",
        "resposta": "Posso te mostrar os especialistas disponíveis agora. Use o filtro Online para encontrar quem pode atender mais rápido.",
        "categoria_slug": "",
        "acao_label": "Ver especialistas online",
        "acao_url": "/especialistas"
    },
    {
        "intencao": "fallback",
        "gatilhos": "",
        "resposta": "Sou o Severino, seu ajudante aqui no Tele-Severino. Me conte em poucas palavras o que você precisa, por exemplo: arrumar chuveiro, ajuda com computador, receita ou estudo.",
        "categoria_slug": "",
        "acao_label": "Ver todos especialistas",
        "acao_url": "/especialistas"
    }
]


def garantir_respostas_severino():
    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS severino_respostas (
                id_resposta INT AUTO_INCREMENT PRIMARY KEY,
                intencao VARCHAR(80) NOT NULL UNIQUE,
                gatilhos TEXT NULL,
                resposta TEXT NOT NULL,
                categoria_slug VARCHAR(80) NULL,
                acao_label VARCHAR(120) NULL,
                acao_url VARCHAR(255) NULL,
                ativo TINYINT(1) NOT NULL DEFAULT 1,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        for item in SEVERINO_RESPOSTAS_PADRAO:
            cursor.execute("""
                INSERT INTO severino_respostas
                (intencao, gatilhos, resposta, categoria_slug, acao_label, acao_url, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, 1)
                ON DUPLICATE KEY UPDATE
                    gatilhos = VALUES(gatilhos),
                    resposta = VALUES(resposta),
                    categoria_slug = VALUES(categoria_slug),
                    acao_label = VALUES(acao_label),
                    acao_url = VALUES(acao_url),
                    ativo = 1
            """, (
                item["intencao"],
                item["gatilhos"],
                item["resposta"],
                item["categoria_slug"],
                item["acao_label"],
                item["acao_url"]
            ))

        conexao.commit()

    except Exception as erro:
        print("Erro ao preparar respostas do Severino:", erro)

    finally:
        if conexao:
            conexao.close()


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
            e.tags, e.status_atendimento, e.plano_disponibilidade
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
            resumo_avaliacao = consultar_resumo_avaliacoes(row["id_usuario"])
            status_info = obter_status_label(row.get("status_atendimento"))
            plano = row.get("plano_disponibilidade") or "FREE"

            db_specialists.append({
                "id": row["id_usuario"],
                "name": nome,
                "initials": initials,
                "role": row["especialidade"],
                "price": format_price(row["valor_minuto"]),
                "price_value": float(row["valor_minuto"] or 0),
                "rating": resumo_avaliacao["rating"],
                "reviews": resumo_avaliacao["reviews"],
                "avatar_class": "avatar-orange",
                "foto_perfil": row.get("foto_perfil"),
                "status_atendimento": status_info["status"],
                "status_label": status_info["label"],
                "is_online": status_info["is_online"],
                "plano_disponibilidade": plano,
                "plano_label": obter_plano_label(plano),
                "about": descricao,
                "category": row.get("categoria") or obter_nome_categoria(categoria_slug),
                "category_slug": categoria_slug,
                "reviews_list": consultar_avaliacoes_especialista(row["id_usuario"]),
                "tags": separar_tags(row.get("tags"), row["especialidade"])
            })

        return db_specialists

    except Exception as erro:
        print(f"Erro ao buscar especialistas do banco: {erro}")
        return []

    finally:
        if conexao:
            conexao.close()



def montar_categorias_dinamicas(especialistas):
    categorias_base = []
    slugs_adicionados = set()

    for categoria in categories:
        categorias_base.append(categoria)
        slugs_adicionados.add(categoria["slug"])

    for especialista in especialistas:
        slug = especialista.get("category_slug")
        nome = especialista.get("category")

        if not slug or slug in slugs_adicionados:
            continue

        categorias_base.append({
            "name": nome or obter_nome_categoria(slug),
            "slug": slug,
            "icon": "•",
            "tone": "blue"
        })

        slugs_adicionados.add(slug)

    return categorias_base


def get_specialist(specialist_id: int):
    db_specialists = get_db_specialists()

    return next(
        (item for item in db_specialists if item["id"] == specialist_id),
        None
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



def consultar_usuario_basico(id_usuario: int):
    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_usuario,
                nome,
                email,
                tipo
            FROM usuarios
            WHERE id_usuario = %s
            LIMIT 1
        """, (id_usuario,))

        usuario = cursor.fetchone()

        if not usuario:
            return {
                "id": id_usuario,
                "nome": "Cliente",
                "email": "",
                "tipo": "CLIENTE",
                "iniciais": "CL",
                "foto_perfil": ""
            }

        nome = usuario.get("nome") or "Cliente"
        partes_nome = [parte for parte in nome.split() if parte]
        iniciais = "".join([parte[0] for parte in partes_nome[:2]]).upper() or "CL"

        return {
            "id": usuario.get("id_usuario"),
            "nome": nome,
            "email": usuario.get("email") or "",
            "tipo": usuario.get("tipo") or "CLIENTE",
            "iniciais": iniciais,
            "foto_perfil": ""
        }

    except Exception as erro:
        print("Erro ao consultar usuário básico:", erro)

        return {
            "id": id_usuario,
            "nome": "Cliente",
            "email": "",
            "tipo": "CLIENTE",
            "iniciais": "CL",
            "foto_perfil": ""
        }

    finally:
        if conexao:
            conexao.close()


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




def garantir_tabela_solicitacoes_atendimento():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitacoes_atendimento (
            id_solicitacao INT AUTO_INCREMENT PRIMARY KEY,
            id_cliente INT NOT NULL,
            id_especialista INT NOT NULL,
            dia_label VARCHAR(80) NOT NULL,
            horario VARCHAR(20) NOT NULL,
            status ENUM('PENDENTE','ACEITA','RECUSADA','EXPIRADA','CANCELADA') NOT NULL DEFAULT 'PENDENTE',
            observacao VARCHAR(255) NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    cursor.execute("SHOW COLUMNS FROM solicitacoes_atendimento LIKE 'cupom_codigo'")
    if not cursor.fetchone():
        cursor.execute("""
            ALTER TABLE solicitacoes_atendimento
            ADD COLUMN cupom_codigo VARCHAR(30) NULL AFTER status
        """)

    cursor.execute("SHOW COLUMNS FROM solicitacoes_atendimento LIKE 'cupom_desconto_percentual'")
    if not cursor.fetchone():
        cursor.execute("""
            ALTER TABLE solicitacoes_atendimento
            ADD COLUMN cupom_desconto_percentual DECIMAL(5,2) NOT NULL DEFAULT 0 AFTER cupom_codigo
        """)


    cursor.execute("""
        ALTER TABLE solicitacoes_atendimento
        MODIFY COLUMN status ENUM('PENDENTE','ACEITA','RECUSADA','EXPIRADA','CANCELADA') NOT NULL DEFAULT 'PENDENTE'
    """)

    cursor.execute("SHOW COLUMNS FROM solicitacoes_atendimento LIKE 'data_expiracao'")
    if not cursor.fetchone():
        cursor.execute("""
            ALTER TABLE solicitacoes_atendimento
            ADD COLUMN data_expiracao DATETIME NULL AFTER horario
        """)

    conexao.commit()
    cursor.close()
    conexao.close()




def atualizar_solicitacoes_expiradas():
    garantir_tabela_solicitacoes_atendimento()

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE solicitacoes_atendimento
        SET status = 'EXPIRADA',
            observacao = 'Solicitação expirada automaticamente por falta de resposta do especialista.'
        WHERE status = 'PENDENTE'
          AND data_expiracao IS NOT NULL
          AND data_expiracao <= NOW()
    """)

    conexao.commit()
    cursor.close()
    conexao.close()


def existe_solicitacao_pendente_cliente_especialista(id_cliente: int, id_especialista: int):
    atualizar_solicitacoes_expiradas()

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM solicitacoes_atendimento
        WHERE id_cliente = %s
          AND id_especialista = %s
          AND status = 'PENDENTE'
    """, (id_cliente, id_especialista))

    resultado = cursor.fetchone() or {"total": 0}

    cursor.close()
    conexao.close()

    return int(resultado["total"] or 0) > 0


def consultar_solicitacoes_cliente(id_cliente: int, limite: int = 30):
    atualizar_solicitacoes_expiradas()

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.id_solicitacao,
            s.id_cliente,
            s.id_especialista,
            s.dia_label,
            s.horario,
            s.status,
            s.cupom_codigo,
            s.cupom_desconto_percentual,
            s.observacao,
            s.data_criacao,
            s.data_expiracao,
            u.nome AS especialista_nome,
            u.email AS especialista_email
        FROM solicitacoes_atendimento s
        LEFT JOIN usuarios u ON u.id_usuario = s.id_especialista
        WHERE s.id_cliente = %s
        ORDER BY s.data_criacao DESC
        LIMIT %s
    """, (id_cliente, limite))

    solicitacoes = cursor.fetchall() or []

    cursor.close()
    conexao.close()

    for solicitacao in solicitacoes:
        data_criacao = solicitacao.get("data_criacao")
        data_expiracao = solicitacao.get("data_expiracao")

        solicitacao["data_criacao_formatada"] = data_criacao.strftime("%d/%m/%Y às %H:%M") if data_criacao else ""
        solicitacao["data_expiracao_formatada"] = data_expiracao.strftime("%d/%m/%Y às %H:%M") if data_expiracao else ""

        status = solicitacao.get("status")

        if status == "PENDENTE":
            solicitacao["status_titulo"] = "Aguardando resposta"
            solicitacao["status_descricao"] = "O especialista tem até 2 horas para aceitar ou recusar. Se não responder, a solicitação expira e você poderá solicitar novamente."
        elif status == "ACEITA":
            solicitacao["status_titulo"] = "Atendimento confirmado"
            solicitacao["status_descricao"] = "Aguarde o especialista iniciar a sala no horário combinado."
        elif status == "RECUSADA":
            solicitacao["status_titulo"] = "Solicitação recusada"
            solicitacao["status_descricao"] = "Você pode escolher outro horário ou procurar outro especialista."
        elif status == "EXPIRADA":
            solicitacao["status_titulo"] = "Solicitação expirada"
            solicitacao["status_descricao"] = "O especialista não respondeu dentro do prazo. Você pode solicitar novamente para este especialista ou escolher outro profissional."
        elif status == "CANCELADA":
            solicitacao["status_titulo"] = "Solicitação cancelada"
            solicitacao["status_descricao"] = "Você cancelou esta solicitação. Se ainda precisar, pode solicitar novamente para este especialista."
        else:
            solicitacao["status_titulo"] = status or "Status"
            solicitacao["status_descricao"] = ""

    return solicitacoes



def cancelar_solicitacao_cliente(id_solicitacao: int, id_cliente: int):
    atualizar_solicitacoes_expiradas()

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT id_solicitacao, status
        FROM solicitacoes_atendimento
        WHERE id_solicitacao = %s
          AND id_cliente = %s
        LIMIT 1
    """, (id_solicitacao, id_cliente))

    solicitacao = cursor.fetchone()

    if not solicitacao:
        cursor.close()
        conexao.close()
        return False, "Solicitação não encontrada."

    if solicitacao["status"] != "PENDENTE":
        cursor.close()
        conexao.close()
        return False, "Somente solicitações pendentes podem ser canceladas."

    cursor.execute("""
        UPDATE solicitacoes_atendimento
        SET status = 'CANCELADA',
            observacao = 'Solicitação cancelada pelo cliente.'
        WHERE id_solicitacao = %s
          AND id_cliente = %s
          AND status = 'PENDENTE'
    """, (id_solicitacao, id_cliente))

    conexao.commit()
    cursor.close()
    conexao.close()

    return True, "Solicitação cancelada com sucesso."


def cupom_primeiro_atendimento_disponivel(id_cliente: int, id_especialista: int = 0):
    atualizar_solicitacoes_expiradas()

    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM solicitacoes_atendimento
        WHERE id_cliente = %s
          AND cupom_codigo = 'PRIMEIRA5'
          AND status = 'ACEITA'
    """, (id_cliente,))

    resultado = cursor.fetchone() or {"total": 0}

    cursor.close()
    conexao.close()

    return int(resultado["total"] or 0) == 0


def criar_solicitacao_atendimento(
    id_cliente: int,
    id_especialista: int,
    dia_label: str,
    horario: str,
    cupom_codigo: str = None,
    cupom_desconto_percentual: float = 0
):
    garantir_tabela_solicitacoes_atendimento()

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO solicitacoes_atendimento
            (
                id_cliente,
                id_especialista,
                dia_label,
                horario,
                data_expiracao,
                status,
                cupom_codigo,
                cupom_desconto_percentual,
                observacao
            )
        VALUES
            (%s, %s, %s, %s, DATE_ADD(NOW(), INTERVAL 2 HOUR), 'PENDENTE', %s, %s, %s)
    """, (
        id_cliente,
        id_especialista,
        dia_label,
        horario,
        cupom_codigo,
        cupom_desconto_percentual,
        "Solicitação criada pelo cliente no perfil público do especialista."
    ))

    conexao.commit()
    id_solicitacao = cursor.lastrowid

    cursor.close()
    conexao.close()

    return id_solicitacao


@app.get("/api/cupom-primeiro-atendimento/status")
def api_status_cupom_primeiro_atendimento(request: Request, especialista_id: int = 0):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return JSONResponse(
            {"ok": False, "disponivel": False, "erro": "Faça login para consultar o cupom."},
            status_code=401
        )

    if usuario["tipo"] != "CLIENTE":
        return JSONResponse(
            {"ok": False, "disponivel": False, "erro": "Cupom disponível apenas para usuário comum."},
            status_code=403
        )

    disponivel = cupom_primeiro_atendimento_disponivel(int(usuario["id"]))

    return {
        "ok": True,
        "codigo": "PRIMEIRA5",
        "desconto_percentual": 5,
        "disponivel": disponivel,
        "mensagem": "Cupom PRIMEIRA5 disponível para seu primeiro atendimento na plataforma." if disponivel else "Cupom PRIMEIRA5 já utilizado no seu histórico."
    }


@app.post("/api/solicitacoes-atendimento")
async def api_criar_solicitacao_atendimento(request: Request):
    atualizar_solicitacoes_expiradas()

    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return JSONResponse(
            {"ok": False, "erro": "Faça login para solicitar atendimento."},
            status_code=401
        )

    if usuario["tipo"] != "CLIENTE":
        return JSONResponse(
            {"ok": False, "erro": "Somente clientes podem solicitar atendimento."},
            status_code=403
        )

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            {"ok": False, "erro": "Dados inválidos para solicitação."},
            status_code=400
        )

    id_especialista = int(payload.get("id_especialista") or 0)
    dia_label = str(payload.get("dia_label") or "").strip()
    horario = str(payload.get("horario") or "").strip()
    cupom_codigo = str(payload.get("cupom_codigo") or "").strip().upper()

    if not id_especialista or not dia_label or not horario:
        return JSONResponse(
            {"ok": False, "erro": "Selecione um dia e horário antes de solicitar."},
            status_code=400
        )

    if existe_solicitacao_pendente_cliente_especialista(int(usuario["id"]), id_especialista):
        return JSONResponse(
            {
                "ok": False,
                "erro": "Você já possui uma solicitação pendente para este especialista. Aguarde a resposta ou o prazo de expiração."
            },
            status_code=400
        )

    cupom_desconto_percentual = 0

    if cupom_codigo:
        if cupom_codigo != "PRIMEIRA5":
            return JSONResponse(
                {"ok": False, "erro": "Cupom inválido. Use PRIMEIRA5 para o primeiro atendimento na plataforma."},
                status_code=400
            )

        if not cupom_primeiro_atendimento_disponivel(int(usuario["id"])):
            return JSONResponse(
                {"ok": False, "erro": "Você já utilizou o cupom PRIMEIRA5 no seu primeiro atendimento."},
                status_code=400
            )

        cupom_desconto_percentual = 5

    id_solicitacao = criar_solicitacao_atendimento(
        int(usuario["id"]),
        id_especialista,
        dia_label,
        horario,
        cupom_codigo or None,
        cupom_desconto_percentual
    )

    return {
        "ok": True,
        "id_solicitacao": id_solicitacao,
        "mensagem": "Solicitação enviada com sucesso. O especialista tem até 2 horas para aceitar ou recusar.",
        "status": "PENDENTE",
        "expira_em": "2 horas",
        "cupom_codigo": cupom_codigo or None,
        "cupom_desconto_percentual": cupom_desconto_percentual
    }


@app.post("/cliente/solicitacoes/{id_solicitacao}/cancelar")
def cliente_cancelar_solicitacao(request: Request, id_solicitacao: int):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "CLIENTE":
        return RedirectResponse(url="/login", status_code=303)

    cancelar_solicitacao_cliente(id_solicitacao, int(usuario["id"]))

    return RedirectResponse(url="/cliente/solicitacoes", status_code=303)


@app.get("/cliente/solicitacoes")
def cliente_solicitacoes(request: Request):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] != "CLIENTE":
        return RedirectResponse(url="/login", status_code=303)

    solicitacoes = consultar_solicitacoes_cliente(int(usuario["id"]))

    return templates.TemplateResponse(
        "cliente_solicitacoes.html",
        {
            "request": request,
            "usuario": usuario,
            "solicitacoes": solicitacoes
        }
    )


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
            "cliente_atual": consultar_cliente_atual_para_layout(int(usuario["id"])),
            "especialista": consultar_especialista_por_usuario(int(usuario["id"])),
            "solicitacoes_atendimento": consultar_solicitacoes_especialista(int(usuario["id"])),
            "solicitacoes_pendentes": contar_solicitacoes_pendentes_especialista(int(usuario["id"])),
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
            "categories": montar_categorias_dinamicas(get_db_specialists()),
            "specialists": get_db_specialists(),
            "cadastro_complementar": consultar_cadastro_complementar(int(usuario["id"]))
        }
    )


@app.get("/especialistas", name="specialist.especialistas")
def especialistas_page(
    request: Request,
    categoria: str = "",
    q: str = "",
    ordenacao: str = ""
):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    todos_especialistas = get_db_specialists()
    categorias_dinamicas = montar_categorias_dinamicas(todos_especialistas)
    categoria_selecionada = normalizar_texto_categoria(categoria)
    termo_busca = str(q or "").strip()
    termo_normalizado = normalizar_texto_categoria(termo_busca)

    specialists_filtrados = todos_especialistas

    if categoria_selecionada:
        specialists_filtrados = [
            specialist for specialist in specialists_filtrados
            if specialist.get("category_slug") == categoria_selecionada
        ]

    if termo_normalizado:
        def corresponde_busca(specialist):
            campos = [
                specialist.get("name", ""),
                specialist.get("role", ""),
                specialist.get("about", ""),
                specialist.get("category", ""),
                specialist.get("category_slug", ""),
                " ".join(specialist.get("tags", []))
            ]

            texto_busca = normalizar_texto_categoria(" ".join(campos))
            return termo_normalizado in texto_busca

        specialists_filtrados = [
            specialist for specialist in specialists_filtrados
            if corresponde_busca(specialist)
        ]

    if ordenacao == "menor_preco":
        specialists_filtrados = sorted(
            specialists_filtrados,
            key=lambda specialist: float(specialist.get("price_value") or 0)
        )
    elif ordenacao == "maior_preco":
        specialists_filtrados = sorted(
            specialists_filtrados,
            key=lambda specialist: float(specialist.get("price_value") or 0),
            reverse=True
        )

    if categoria_selecionada:
        nome_categoria = obter_nome_categoria(categoria_selecionada)
        title = nome_categoria
        subtitle = f"Especialistas disponíveis em {nome_categoria}"
    else:
        title = "Especialistas"
        subtitle = "Escolha um profissional disponível"

    if termo_busca:
        subtitle = f'Resultados para "{termo_busca}"'

    return templates.TemplateResponse(
        "especialistas.html",
        {
            "request": request,
            "title": title,
            "subtitle": subtitle,
            "specialists": specialists_filtrados,
            "categories": categories,
            "categoria_selecionada": categoria_selecionada,
            "q": termo_busca,
            "ordenacao": ordenacao,
            "cliente_atual": consultar_cliente_atual_para_layout(int(usuario["id"]))
        }
    )


@app.get("/perfil/{specialist_id}", name="specialist.especialista")
def perfil(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    specialist = get_specialist(specialist_id)

    if not specialist:
        return RedirectResponse("/especialistas", status_code=303)

    return templates.TemplateResponse(
        "perfil.html",
        {
            "request": request,
            "specialist": specialist,
            "agenda": montar_agenda_disponibilidade(specialist.get("plano_disponibilidade"))
        }
    )


@app.get("/chamada/{specialist_id}", name="call.chamada")
def chamada(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    specialist = get_specialist(specialist_id)

    if not specialist:
        return RedirectResponse("/especialistas", status_code=303)

    return templates.TemplateResponse(
        "chamada.html",
        {
            "request": request,
            "specialist": specialist
        }
    )


@app.get("/pagamento/{specialist_id}", name="payment.pagamento")
def pagamento(request: Request, specialist_id: int, tempo: int = 15):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    specialist = get_specialist(specialist_id)

    if not specialist:
        return RedirectResponse("/especialistas", status_code=303)

    payment_summary = montar_resumo_pagamento(specialist, tempo)
    payment_profile = get_fake_payment_profile(usuario)

    return templates.TemplateResponse(
        "pagamento.html",
        {
            "request": request,
            "specialist": specialist,
            "payment_summary": payment_summary,
            "payment_profile": payment_profile,
            "erro": None
        }
    )


@app.post("/pagamento/{specialist_id}", name="payment.confirmar")
def confirmar_pagamento(
    request: Request,
    specialist_id: int,
    payment_method: str = Form(...),
    gateway_status: str = Form(""),
    duration_seconds: int = Form(15)
):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    specialist = get_specialist(specialist_id)

    if not specialist:
        return RedirectResponse("/especialistas", status_code=303)

    payment_summary = montar_resumo_pagamento(specialist, duration_seconds)
    payment_profile = get_fake_payment_profile(usuario)

    metodos_validos = {
        "cartao": "Cartão de crédito",
        "pix": "PIX"
    }

    if payment_method not in metodos_validos:
        return templates.TemplateResponse(
            "pagamento.html",
            {
                "request": request,
                "specialist": specialist,
                "payment_summary": payment_summary,
                "payment_profile": payment_profile,
                "erro": "Selecione uma forma de pagamento válida."
            },
            status_code=400
        )

    if payment_method == "cartao" and not payment_profile["has_saved_card"]:
        return templates.TemplateResponse(
            "pagamento.html",
            {
                "request": request,
                "specialist": specialist,
                "payment_summary": payment_summary,
                "payment_profile": payment_profile,
                "erro": "Nenhum cartão salvo foi encontrado para este usuário."
            },
            status_code=400
        )

    if gateway_status != "approved":
        return templates.TemplateResponse(
            "pagamento.html",
            {
                "request": request,
                "specialist": specialist,
                "payment_summary": payment_summary,
                "payment_profile": payment_profile,
                "erro": "Aguardando confirmação fake da operadora de pagamento."
            },
            status_code=400
        )

    transaction_id = f"fake-{usuario['id']}-{specialist_id}-{payment_method}"

    response = RedirectResponse(
        f"/avaliacao/{specialist_id}?pagamento=aprovado&metodo={payment_method}&transacao={transaction_id}",
        status_code=303
    )
    response.set_cookie(
        payment_cookie_name(usuario["id"], specialist_id),
        transaction_id,
        max_age=1800,
        httponly=True
    )

    return response


@app.get("/avaliacao/{specialist_id}", name="review.avaliacao")
def avaliacao(request: Request, specialist_id: int):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    pagamento_cookie = request.cookies.get(payment_cookie_name(usuario["id"], specialist_id))

    if not pagamento_cookie:
        return RedirectResponse(f"/pagamento/{specialist_id}", status_code=303)

    specialist = get_specialist(specialist_id)

    if not specialist:
        return RedirectResponse("/especialistas", status_code=303)

    return templates.TemplateResponse(
        "avaliacao.html",
        {
            "request": request,
            "specialist": specialist
        }
    )


@app.post("/avaliacao/{specialist_id}")
def enviar_avaliacao(
    request: Request,
    specialist_id: int,
    rating: int = Form(...),
    comment: str = Form("")
):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    pagamento_cookie = request.cookies.get(payment_cookie_name(usuario["id"], specialist_id))

    if not pagamento_cookie:
        return RedirectResponse(f"/pagamento/{specialist_id}", status_code=303)

    salvar_avaliacao_especialista(
        id_cliente=int(usuario["id"]),
        id_especialista=int(specialist_id),
        nota=int(rating),
        comentario=comment.strip()
    )

    response = RedirectResponse("/home", status_code=303)
    response.delete_cookie(payment_cookie_name(usuario["id"], specialist_id))
    return response




@app.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        "admin_login.html",
        {
            "request": request,
            "erro": ""
        }
    )


@app.post("/admin/login-web")
def admin_login_web(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    usuario = consultar_usuarios(email)

    if usuario is None or isinstance(usuario, dict):
        return templates.TemplateResponse(
            "admin_login.html",
            {
                "request": request,
                "erro": "E-mail ou senha inválidos."
            }
        )

    id_usuario = usuario[0]
    senha_banco = usuario[3]
    tipo_usuario = usuario[4]

    if senha_hash(password) != senha_banco:
        return templates.TemplateResponse(
            "admin_login.html",
            {
                "request": request,
                "erro": "E-mail ou senha inválidos."
            }
        )

    if tipo_usuario not in ["ADMIN", "SUPER_ADMIN"]:
        return templates.TemplateResponse(
            "admin_login.html",
            {
                "request": request,
                "erro": "Este acesso é exclusivo para administradores."
            }
        )

    response = RedirectResponse("/personalizacao", status_code=303)
    response.set_cookie("usuario_id", str(id_usuario))
    response.set_cookie("usuario_tipo", tipo_usuario)

    return response


def exigir_admin(request: Request):
    usuario = exigir_login(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    if usuario["tipo"] == "CLIENTE":
        return RedirectResponse("/cliente/perfil", status_code=303)

    if usuario["tipo"] == "ESPECIALISTA":
        return RedirectResponse(
            f"/especialista/dashboard?usuario_id={usuario['id']}",
            status_code=303
        )

    if usuario["tipo"] not in ["ADMIN", "SUPER_ADMIN"]:
        return RedirectResponse("/login", status_code=303)

    return usuario


@app.get("/personalizacao", name="brand.personalizacao")
def personalizacao(request: Request):
    usuario = exigir_admin(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    return templates.TemplateResponse(
        "personalizacao.html",
        {
            "request": request,
            "usuario_admin": usuario,
            "is_super_admin": usuario["tipo"] == "SUPER_ADMIN"
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
            "solicitacoes_atendimento": consultar_solicitacoes_especialista(int(usuario["id"])),
            "solicitacoes_pendentes": contar_solicitacoes_pendentes_especialista(int(usuario["id"])),
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



def consultar_resposta_severino(mensagem):
    garantir_respostas_severino()

    mensagem_normalizada = normalizar_texto_categoria(mensagem)

    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                intencao,
                gatilhos,
                resposta,
                categoria_slug,
                acao_label,
                acao_url
            FROM severino_respostas
            WHERE ativo = 1
            ORDER BY
                CASE WHEN intencao = 'fallback' THEN 2 ELSE 1 END,
                id_resposta ASC
        """)

        respostas = cursor.fetchall()

        fallback = None
        melhor_resposta = None
        melhor_pontuacao = 0

        for item in respostas:
            if item.get("intencao") == "fallback":
                fallback = item
                continue

            gatilhos = item.get("gatilhos") or ""
            pontuacao = 0

            for gatilho in gatilhos.split(","):
                gatilho_normalizado = normalizar_texto_categoria(gatilho)

                if gatilho_normalizado and gatilho_normalizado in mensagem_normalizada:
                    pontuacao += 1

            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_resposta = item

        resposta_final = melhor_resposta or fallback

        if not resposta_final:
            return {
                "intencao": "fallback",
                "resposta": "Sou o Severino, seu ajudante aqui no Tele-Severino. Me conte em poucas palavras o que você precisa.",
                "categoria_slug": "",
                "acao_label": "Ver especialistas",
                "acao_url": "/especialistas"
            }

        return {
            "intencao": resposta_final.get("intencao") or "fallback",
            "resposta": resposta_final.get("resposta") or "",
            "categoria_slug": resposta_final.get("categoria_slug") or "",
            "acao_label": resposta_final.get("acao_label") or "Ver especialistas",
            "acao_url": resposta_final.get("acao_url") or "/especialistas"
        }

    except Exception as erro:
        print("Erro ao consultar Severino:", erro)

        return {
            "intencao": "fallback",
            "resposta": "Sou o Severino, seu ajudante aqui no Tele-Severino. No momento não consegui entender tudo, mas posso te mostrar os especialistas disponíveis.",
            "categoria_slug": "",
            "acao_label": "Ver especialistas",
            "acao_url": "/especialistas"
        }

    finally:
        if conexao:
            conexao.close()


@app.post("/api/severino/chat")
async def severino_chat(request: Request):
    try:
        dados = await request.json()
    except Exception:
        dados = {}

    mensagem = (dados.get("mensagem") or "").strip()

    if not mensagem:
        return JSONResponse({
            "ok": False,
            "resposta": "Me conte em poucas palavras o que você precisa. Por exemplo: arrumar chuveiro, ajuda com computador, receita ou estudos.",
            "acao_label": "Ver especialistas",
            "acao_url": "/especialistas"
        })

    resposta = consultar_resposta_severino(mensagem)

    return JSONResponse({
        "ok": True,
        "mensagem": mensagem,
        **resposta
    })


def garantir_tabela_cliente_perfil():
    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cliente_perfil_config (
                id_config INT AUTO_INCREMENT PRIMARY KEY,
                id_usuario INT NOT NULL UNIQUE,
                nome_exibicao VARCHAR(160) NULL,
                objetivo TEXT NULL,
                foto_perfil VARCHAR(255) NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)

        conexao.commit()

    except Exception as erro:
        print("Erro ao garantir tabela cliente_perfil_config:", erro)

    finally:
        if conexao:
            conexao.close()


def consultar_perfil_cliente_config(id_usuario: int):
    garantir_tabela_cliente_perfil()

    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                nome_exibicao,
                objetivo,
                foto_perfil
            FROM cliente_perfil_config
            WHERE id_usuario = %s
            LIMIT 1
        """, (id_usuario,))

        return cursor.fetchone() or {}

    except Exception as erro:
        print("Erro ao consultar perfil do cliente:", erro)
        return {}

    finally:
        if conexao:
            conexao.close()


def salvar_perfil_cliente_config(id_usuario: int, nome_exibicao=None, objetivo=None, foto_perfil=None):
    garantir_tabela_cliente_perfil()

    atual = consultar_perfil_cliente_config(id_usuario)

    nome_final = nome_exibicao if nome_exibicao is not None else atual.get("nome_exibicao")
    objetivo_final = objetivo if objetivo is not None else atual.get("objetivo")
    foto_final = foto_perfil if foto_perfil is not None else atual.get("foto_perfil")

    conexao = None

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO cliente_perfil_config
                (id_usuario, nome_exibicao, objetivo, foto_perfil)
            VALUES
                (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nome_exibicao = VALUES(nome_exibicao),
                objetivo = VALUES(objetivo),
                foto_perfil = VALUES(foto_perfil)
        """, (
            id_usuario,
            nome_final,
            objetivo_final,
            foto_final
        ))

        conexao.commit()

    except Exception as erro:
        print("Erro ao salvar perfil do cliente:", erro)

    finally:
        if conexao:
            conexao.close()


def consultar_cliente_atual_para_layout(id_usuario: int):
    usuario = consultar_usuario_basico(id_usuario)
    perfil = consultar_perfil_cliente_config(id_usuario)

    nome_base = usuario.get("nome") or "Cliente"
    nome_final = perfil.get("nome_exibicao") or nome_base

    partes_nome = [parte for parte in nome_final.split() if parte]
    iniciais = "".join([parte[0] for parte in partes_nome[:2]]).upper() or "CL"

    usuario["nome"] = nome_final
    usuario["iniciais"] = iniciais
    usuario["foto_perfil"] = perfil.get("foto_perfil") or ""
    usuario["objetivo"] = perfil.get("objetivo") or ""

    return usuario


@app.get("/cliente/perfil")
def cliente_perfil_page(request: Request):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    cliente_atual = consultar_cliente_atual_para_layout(int(usuario["id"]))

    return templates.TemplateResponse(
        "cliente_perfil.html",
        {
            "request": request,
            "usuario_id": usuario["id"],
            "cliente_atual": cliente_atual
        }
    )


@app.post("/cliente/perfil/dados")
def cliente_perfil_dados(
    request: Request,
    nome_exibicao: str = Form(""),
    objetivo: str = Form("")
):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    salvar_perfil_cliente_config(
        int(usuario["id"]),
        nome_exibicao=nome_exibicao.strip() or None,
        objetivo=objetivo.strip() or None
    )

    return RedirectResponse("/cliente/perfil", status_code=303)


@app.post("/cliente/perfil/foto")
async def cliente_perfil_foto(
    request: Request,
    foto_perfil: UploadFile = File(...)
):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    nome_original = foto_perfil.filename or ""
    extensao = os.path.splitext(nome_original)[1].lower()

    if extensao not in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
        extensao = ".png"

    pasta_upload = "View/static/uploads/clientes"
    os.makedirs(pasta_upload, exist_ok=True)

    nome_arquivo = f"cliente_{usuario['id']}_{uuid.uuid4().hex}{extensao}"
    caminho_arquivo = os.path.join(pasta_upload, nome_arquivo)

    conteudo = await foto_perfil.read()

    with open(caminho_arquivo, "wb") as arquivo:
        arquivo.write(conteudo)

    caminho_publico = f"/static/uploads/clientes/{nome_arquivo}"

    salvar_perfil_cliente_config(
        int(usuario["id"]),
        foto_perfil=caminho_publico
    )

    return RedirectResponse("/cliente/perfil", status_code=303)


@app.get("/cliente/mensagens")
def cliente_mensagens_page(request: Request):
    usuario = exigir_cliente(request)

    if isinstance(usuario, RedirectResponse):
        return usuario

    cliente_atual = consultar_cliente_atual_para_layout(int(usuario["id"]))

    especialistas = get_db_specialists()

    conversas = [
        {
            "tipo": "severino",
            "nome": "Severino",
            "subtitulo": "Assistente Tele-Severino",
            "mensagem": "Me conte o que você precisa resolver hoje.",
            "iniciais": "S",
            "status": "online",
            "url": "/home"
        }
    ]

    for especialista in especialistas[:8]:
        conversas.append({
            "tipo": "especialista",
            "nome": especialista.get("name"),
            "subtitulo": especialista.get("role"),
            "mensagem": "Histórico de atendimento e solicitações do cliente.",
            "iniciais": especialista.get("initials"),
            "foto": especialista.get("foto_perfil"),
            "status": "online" if especialista.get("is_online") else "offline",
            "url": f"/perfil/{especialista.get('id')}"
        })

    return templates.TemplateResponse(
        "cliente_mensagens.html",
        {
            "request": request,
            "usuario_id": usuario["id"],
            "cliente_atual": cliente_atual,
            "conversas": conversas
        }
    )
