import sys
import subprocess
from urllib.parse import urljoin

try:
    import requests
except ModuleNotFoundError:
    print("ERRO: biblioteca requests não encontrada.")
    print("Rode: pip install requests")
    sys.exit(1)


BASE_URL = "http://127.0.0.1:8000"
SENHA_PADRAO = "123456"


PERFIS = [
    {
        "nome": "CLIENTE",
        "login_page": "/login",
        "login_post": "/login-web",
        "email": "cliente.navegador@teste.com",
        "senha": SENHA_PADRAO,
        "rotas": [
            "/home",
            "/especialistas",
            "/perfil/4",
            "/cliente/solicitacoes",
            "/cliente/mensagens",
            "/cliente/perfil",
        ],
    },
    {
        "nome": "ESPECIALISTA",
        "login_page": "/login",
        "login_post": "/login-web",
        "email": "especialista.navegador@teste.com",
        "senha": SENHA_PADRAO,
        "rotas": [
            "/especialista/dashboard?usuario_id=4",
        ],
    },
    {
        "nome": "ADMIN",
        "login_page": "/admin/login",
        "login_post": "/admin/login-web",
        "email": "admin.tele@teste.com",
        "senha": SENHA_PADRAO,
        "rotas": [
            "/personalizacao",
        ],
    },
    {
        "nome": "SUPER_ADMIN",
        "login_page": "/admin/login",
        "login_post": "/admin/login-web",
        "email": "super.admin@teste.com",
        "senha": SENHA_PADRAO,
        "rotas": [
            "/personalizacao",
        ],
    },
]


def url(path):
    return urljoin(BASE_URL, path)


def linha():
    print("-" * 72)


def ok(msg):
    print(f"✅ {msg}")


def erro(msg):
    print(f"❌ {msg}")


def aviso(msg):
    print(f"⚠️  {msg}")


def validar_servidor():
    try:
        resposta = requests.get(url("/login"), timeout=8)
    except requests.RequestException as exc:
        erro("Servidor local não respondeu.")
        print(f"Detalhe: {exc}")
        print("\nConfirme se o uvicorn está rodando:")
        print('export GROQ_API_KEY="fake-key-local"')
        print("uvicorn main:app --reload")
        sys.exit(1)

    if resposta.status_code >= 500:
        erro(f"/login retornou {resposta.status_code}")
        sys.exit(1)

    ok("Servidor local respondeu.")


def rodar_seed():
    print("\nPreparando usuários padrão...")
    resultado = subprocess.run(
        [sys.executable, "scripts/seed_usuarios_padrao.py"],
        text=True,
        capture_output=True,
    )

    if resultado.returncode != 0:
        erro("Seed de usuários falhou.")
        print(resultado.stdout)
        print(resultado.stderr)
        sys.exit(1)

    ok("Seed de usuários padrão executado.")
    if resultado.stdout.strip():
        print(resultado.stdout.strip())


def validar_login_e_rotas(perfil):
    linha()
    print(f"Perfil: {perfil['nome']}")
    print(f"E-mail: {perfil['email']}")

    sessao = requests.Session()

    try:
        pagina_login = sessao.get(url(perfil["login_page"]), timeout=8, allow_redirects=True)
    except requests.RequestException as exc:
        erro(f"Não abriu a página de login {perfil['login_page']}")
        print(exc)
        return False

    if pagina_login.status_code >= 500:
        erro(f"{perfil['login_page']} retornou {pagina_login.status_code}")
        return False

    ok(f"Página de login abriu: {perfil['login_page']}")

    try:
        resposta_login = sessao.post(
            url(perfil["login_post"]),
            data={
                "email": perfil["email"],
                "password": perfil["senha"],
            },
            timeout=8,
            allow_redirects=True,
        )
    except requests.RequestException as exc:
        erro(f"Erro ao fazer login em {perfil['login_post']}")
        print(exc)
        return False

    if resposta_login.status_code >= 500:
        erro(f"Login retornou erro {resposta_login.status_code}")
        print(f"URL final: {resposta_login.url}")
        return False

    html_login = resposta_login.text.lower()
    if "e-mail ou senha inválidos" in html_login or "email ou senha inválidos" in html_login:
        erro("Login recusado: e-mail ou senha inválidos.")
        return False

    if "/login" in resposta_login.url and perfil["nome"] not in ["ADMIN", "SUPER_ADMIN"]:
        erro(f"Login parece ter voltado para /login. URL final: {resposta_login.url}")
        return False

    ok(f"Login OK. URL final: {resposta_login.url}")

    tudo_ok = True

    for rota in perfil["rotas"]:
        try:
            resposta_rota = sessao.get(url(rota), timeout=8, allow_redirects=True)
        except requests.RequestException as exc:
            erro(f"{rota} não respondeu.")
            print(exc)
            tudo_ok = False
            continue

        if resposta_rota.status_code >= 500:
            erro(f"{rota} retornou {resposta_rota.status_code}")
            print(f"URL final: {resposta_rota.url}")
            tudo_ok = False
            continue

        if "/login" in resposta_rota.url and rota not in ["/login", "/admin/login"]:
            erro(f"{rota} redirecionou para login. URL final: {resposta_rota.url}")
            tudo_ok = False
            continue

        ok(f"Rota OK: {rota} -> {resposta_rota.status_code}")

    try:
        sessao.get(url("/logout"), timeout=8, allow_redirects=True)
    except requests.RequestException:
        aviso("Não consegui executar logout, mas o teste principal continuou.")

    return tudo_ok


def main():
    print("Teste automático dos fluxos de login e perfis")
    print(f"Base URL: {BASE_URL}")

    validar_servidor()
    rodar_seed()

    resultados = []

    for perfil in PERFIS:
        resultados.append((perfil["nome"], validar_login_e_rotas(perfil)))

    linha()
    print("Resumo:")

    falhas = 0

    for nome, sucesso in resultados:
        if sucesso:
            ok(f"{nome}: aprovado")
        else:
            erro(f"{nome}: falhou")
            falhas += 1

    linha()

    if falhas:
        erro(f"Teste finalizado com {falhas} perfil(is) com falha.")
        sys.exit(1)

    ok("Todos os fluxos principais passaram.")


if __name__ == "__main__":
    main()
