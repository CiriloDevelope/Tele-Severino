import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:
    print("ERRO: Playwright não instalado.")
    print("Rode:")
    print("pip install playwright")
    print("python -m playwright install chromium")
    sys.exit(1)


BASE_URL = "http://127.0.0.1:8000"
REPORT_DIR = Path("reports/visual")
SCREENSHOT_DIR = REPORT_DIR / "screenshots"

REPORT_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


PERFIS = [
    {
        "nome": "PUBLICO",
        "email": None,
        "senha": None,
        "login_page": None,
        "login_post": None,
        "rotas": [
            "/login",
            "/admin/login",
        ],
    },
    {
        "nome": "CLIENTE",
        "email": "cliente.navegador@teste.com",
        "senha": "123456",
        "login_page": "/login",
        "login_post": "/login-web",
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
        "email": "especialista.navegador@teste.com",
        "senha": "123456",
        "login_page": "/login",
        "login_post": "/login-web",
        "rotas": [
            "/especialista/dashboard?usuario_id=4",
        ],
    },
    {
        "nome": "ADMIN",
        "email": "admin.tele@teste.com",
        "senha": "123456",
        "login_page": "/admin/login",
        "login_post": "/admin/login-web",
        "rotas": [
            "/personalizacao",
        ],
    },
    {
        "nome": "SUPER_ADMIN",
        "email": "super.admin@teste.com",
        "senha": "123456",
        "login_page": "/admin/login",
        "login_post": "/admin/login-web",
        "rotas": [
            "/personalizacao",
        ],
    },
]


LIMITES = {
    "titulo_min": 20,
    "subtitulo_min": 14,
    "texto_min": 11,
    "botao_min": 11,
    "input_min": 11,
    "diferenca_light_dark_max": 1.0,
}


def rodar_seed():
    resultado = subprocess.run(
        [sys.executable, "scripts/seed_usuarios_padrao.py"],
        text=True,
        capture_output=True,
    )

    if resultado.returncode != 0:
        print("ERRO: seed falhou.")
        print(resultado.stdout)
        print(resultado.stderr)
        sys.exit(1)

    print("✅ Seed executado.")


def url(rota):
    return BASE_URL + rota


def slug(texto):
    texto = texto.replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")
    texto = re.sub(r"[^a-zA-Z0-9_-]+", "_", texto)
    return texto.strip("_") or "home"


def login(page, perfil):
    if not perfil["email"]:
        return True

    page.goto(url(perfil["login_page"]), wait_until="networkidle")

    page.fill('input[name="email"]', perfil["email"])

    senha_selectors = [
        'input[name="password"]',
        'input[name="senha"]',
        'input[type="password"]',
    ]

    senha_preenchida = False

    for selector in senha_selectors:
        if page.locator(selector).count() > 0:
            page.fill(selector, perfil["senha"])
            senha_preenchida = True
            break

    if not senha_preenchida:
        raise Exception(f"Campo de senha não encontrado em {perfil['login_page']}")

    submit_selectors = [
        'button[type="submit"]',
        'input[type="submit"]',
        'form button',
        '.login-button',
        '.btn-login',
    ]

    clicou_submit = False

    for selector in submit_selectors:
        locator = page.locator(selector)

        if locator.count() > 0:
            locator.first.click()
            clicou_submit = True
            break

    if not clicou_submit:
        page.keyboard.press("Enter")

    page.wait_for_load_state("networkidle")

    return True


def aplicar_tema(page, tema):
    page.evaluate(
        """
        (tema) => {
            const darkClasses = [
                "client-theme-dark",
                "theme-dark",
                "dark-theme",
                "dark",
                "admin-theme-dark"
            ];

            darkClasses.forEach((classe) => {
                document.body.classList.remove(classe);
                document.documentElement.classList.remove(classe);
            });

            if (tema === "dark") {
                darkClasses.forEach((classe) => {
                    document.body.classList.add(classe);
                    document.documentElement.classList.add(classe);
                });
            }

            try {
                localStorage.setItem("teleSeverinoVisualTestTheme", tema);
            } catch (e) {}
        }
        """,
        tema,
    )

    page.wait_for_timeout(250)


def coletar_elementos(page):
    return page.evaluate(
        """
        () => {
            function visible(el) {
                const style = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();

                return (
                    style.display !== "none" &&
                    style.visibility !== "hidden" &&
                    Number(style.opacity) !== 0 &&
                    rect.width > 0 &&
                    rect.height > 0
                );
            }

            function category(el) {
                const tag = el.tagName.toLowerCase();
                const cls = String(el.className || "").toLowerCase();

                if (
                    tag === "h1" ||
                    cls.includes("title") ||
                    cls.includes("titulo") ||
                    cls.includes("heading") ||
                    cls.includes("hero")
                ) {
                    return "titulo";
                }

                if (
                    tag === "h2" ||
                    tag === "h3" ||
                    tag === "h4" ||
                    cls.includes("subtitle") ||
                    cls.includes("subtitulo") ||
                    cls.includes("lead") ||
                    cls.includes("description")
                ) {
                    return "subtitulo";
                }

                if (tag === "button" || cls.includes("btn") || cls.includes("button")) {
                    return "botao";
                }

                if (tag === "input" || tag === "textarea" || tag === "select") {
                    return "input";
                }

                if (tag === "label") {
                    return "label";
                }

                return "texto";
            }

            const selectors = [
                "h1", "h2", "h3", "h4",
                "p", "span", "small", "label", "a",
                "button", "input", "textarea", "select",
                ".page-title", ".page-subtitle",
                ".section-title", ".section-subtitle",
                ".card-title", ".card-subtitle",
                ".client-hero-title", ".client-hero-subtitle"
            ];

            const nodes = Array.from(document.querySelectorAll(selectors.join(",")));

            return nodes
                .filter(visible)
                .filter((el) => {
                    const text = (el.innerText || el.value || el.getAttribute("placeholder") || "").trim();
                    const tag = el.tagName.toLowerCase();
                    const cls = String(el.className || "").toLowerCase();

                    if (!text) return false;

                    const ignoredText = text.length <= 2 && !["button", "input", "textarea", "select"].includes(tag);
                    if (ignoredText) return false;

                    const ignoredClassWords = [
                        "badge", "avatar", "icon", "chip", "tag", "pill", "status",
                        "menu", "nav", "rail", "bottom", "breadcrumb", "rating",
                        "star", "count", "meta", "preview-avatar", "client-message-dock",
                        "logo", "brand", "sidebar", "layout-brand"
                    ];

                    if (ignoredClassWords.some((word) => cls.includes(word))) return false;

                    if (
                        el.closest(".client-message-dock") ||
                        el.closest(".client-instagram-rail") ||
                        el.closest(".mobile-bottom-nav") ||
                        el.closest("nav") ||
                        el.closest("aside") ||
                        el.closest("footer")
                    ) {
                        return false;
                    }

                    return true;
                })
                .map((el, index) => {
                    const style = window.getComputedStyle(el);
                    const rect = el.getBoundingClientRect();
                    const text = (el.innerText || el.value || el.getAttribute("placeholder") || "").trim();

                    return {
                        index,
                        tag: el.tagName.toLowerCase(),
                        classe: String(el.className || ""),
                        categoria: category(el),
                        texto: text.slice(0, 90),
                        fontSize: parseFloat(style.fontSize || "0"),
                        fontWeight: style.fontWeight,
                        lineHeight: style.lineHeight,
                        color: style.color,
                        background: style.backgroundColor,
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                    };
                })
                .filter((item) => item.texto.length > 0);
        }
        """
    )


def chave_elemento(item):
    texto = re.sub(r"\s+", " ", item["texto"]).strip().lower()
    return f'{item["categoria"]}|{item["tag"]}|{texto[:60]}'


def validar_elementos(perfil, rota, tema, elementos):
    problemas = []

    titulos = [e for e in elementos if e["categoria"] == "titulo"]
    subtitulos = [e for e in elementos if e["categoria"] == "subtitulo"]

    if not titulos and rota not in ["/login", "/admin/login"]:
        problemas.append({
            "tipo": "sem_titulo",
            "perfil": perfil,
            "rota": rota,
            "tema": tema,
            "mensagem": "Tela sem título visível identificado.",
        })

    for item in elementos:
        cat = item["categoria"]
        fonte = item["fontSize"]

        minimo = None

        if cat == "titulo":
            minimo = LIMITES["titulo_min"]
        elif cat == "subtitulo":
            minimo = LIMITES["subtitulo_min"]
        elif cat == "botao":
            minimo = LIMITES["botao_min"]
        elif cat == "input":
            minimo = LIMITES["input_min"]
        elif cat in ["texto", "label"]:
            minimo = LIMITES["texto_min"]

        # Botões de ícone usam font-size 0 de propósito e exibem ícone via CSS.
        # Exemplo: botão "Enviar" da conversa, que visualmente é uma seta.
        if cat == "botao" and fonte == 0:
            continue

        if minimo and fonte < minimo:
            problemas.append({
                "tipo": "fonte_pequena",
                "perfil": perfil,
                "rota": rota,
                "tema": tema,
                "categoria": cat,
                "texto": item["texto"],
                "fontSize": fonte,
                "minimo": minimo,
                "mensagem": f"Fonte abaixo do mínimo esperado: {fonte}px < {minimo}px",
            })

    return problemas


def comparar_light_dark(perfil, rota, light, dark):
    problemas = []

    light_map = {chave_elemento(item): item for item in light}
    dark_map = {chave_elemento(item): item for item in dark}

    for chave, item_light in light_map.items():
        item_dark = dark_map.get(chave)

        if not item_dark:
            continue

        diferenca = abs(item_light["fontSize"] - item_dark["fontSize"])

        if diferenca > LIMITES["diferenca_light_dark_max"]:
            problemas.append({
                "tipo": "fonte_diferente_light_dark",
                "perfil": perfil,
                "rota": rota,
                "categoria": item_light["categoria"],
                "texto": item_light["texto"],
                "fontSize_light": item_light["fontSize"],
                "fontSize_dark": item_dark["fontSize"],
                "diferenca": round(diferenca, 2),
                "mensagem": "Mesmo texto com tamanho diferente entre light e dark.",
            })

    return problemas


def validar_rota(page, perfil_nome, rota):
    dados_por_tema = {}
    problemas = []

    page.goto(url(rota), wait_until="networkidle")

    status_text = page.locator("body").inner_text(timeout=5000)

    if "Internal Server Error" in status_text:
        problemas.append({
            "tipo": "erro_500",
            "perfil": perfil_nome,
            "rota": rota,
            "mensagem": "Tela exibiu Internal Server Error.",
        })
        return dados_por_tema, problemas

    for tema in ["light", "dark"]:
        aplicar_tema(page, tema)

        elementos = coletar_elementos(page)
        dados_por_tema[tema] = elementos

        problemas.extend(validar_elementos(perfil_nome, rota, tema, elementos))

        screenshot = SCREENSHOT_DIR / f"{perfil_nome.lower()}__{slug(rota)}__{tema}.png"
        page.screenshot(path=str(screenshot), full_page=True)

    problemas.extend(
        comparar_light_dark(
            perfil_nome,
            rota,
            dados_por_tema.get("light", []),
            dados_por_tema.get("dark", []),
        )
    )

    return dados_por_tema, problemas


def main():
    print("Teste visual automático - fontes, textos, light/dark e rotas")
    print(f"Base URL: {BASE_URL}")

    rodar_seed()

    relatorio = {
        "base_url": BASE_URL,
        "limites": LIMITES,
        "paginas": [],
        "problemas": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for perfil in PERFIS:
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            page = context.new_page()

            print("\n" + "-" * 72)
            print(f"Perfil: {perfil['nome']}")

            try:
                login(page, perfil)
                print("✅ Login/sessão OK")
            except Exception as erro:
                print(f"❌ Falha no login/sessão: {erro}")
                relatorio["problemas"].append({
                    "tipo": "falha_login",
                    "perfil": perfil["nome"],
                    "mensagem": str(erro),
                })
                context.close()
                continue

            for rota in perfil["rotas"]:
                print(f"Validando: {rota}")

                try:
                    dados, problemas = validar_rota(page, perfil["nome"], rota)
                except Exception as erro:
                    print(f"❌ Erro ao validar rota {rota}: {erro}")
                    relatorio["problemas"].append({
                        "tipo": "erro_teste",
                        "perfil": perfil["nome"],
                        "rota": rota,
                        "mensagem": str(erro),
                    })
                    continue

                relatorio["paginas"].append({
                    "perfil": perfil["nome"],
                    "rota": rota,
                    "elementos_light": len(dados.get("light", [])),
                    "elementos_dark": len(dados.get("dark", [])),
                })

                if problemas:
                    print(f"⚠️  {len(problemas)} ponto(s) encontrados")
                else:
                    print("✅ OK")

                relatorio["problemas"].extend(problemas)

            context.close()

        browser.close()

    json_path = REPORT_DIR / "visual_font_report.json"
    json_path.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2))

    html_path = REPORT_DIR / "visual_font_report.html"
    html_path.write_text(gerar_html(relatorio), encoding="utf-8")

    print("\n" + "=" * 72)
    print("Resumo final")

    if relatorio["problemas"]:
        print(f"⚠️  Encontrados {len(relatorio['problemas'])} ponto(s) para revisar.")
        print(f"Relatório JSON: {json_path}")
        print(f"Relatório HTML: {html_path}")
        sys.exit(1)

    print("✅ Nenhum problema visual crítico encontrado.")
    print(f"Relatório JSON: {json_path}")
    print(f"Relatório HTML: {html_path}")


def gerar_html(relatorio):
    linhas = []

    for problema in relatorio["problemas"]:
        linhas.append(f"""
        <tr>
          <td>{problema.get("tipo", "")}</td>
          <td>{problema.get("perfil", "")}</td>
          <td>{problema.get("rota", "")}</td>
          <td>{problema.get("tema", "")}</td>
          <td>{problema.get("categoria", "")}</td>
          <td>{problema.get("fontSize", problema.get("fontSize_light", ""))}</td>
          <td>{problema.get("fontSize_dark", "")}</td>
          <td>{problema.get("texto", "")}</td>
          <td>{problema.get("mensagem", "")}</td>
        </tr>
        """)

    if not linhas:
        linhas.append("""
        <tr>
          <td colspan="9">Nenhum problema visual crítico encontrado.</td>
        </tr>
        """)

    paginas = []

    for pagina in relatorio["paginas"]:
        paginas.append(f"""
        <tr>
          <td>{pagina["perfil"]}</td>
          <td>{pagina["rota"]}</td>
          <td>{pagina["elementos_light"]}</td>
          <td>{pagina["elementos_dark"]}</td>
        </tr>
        """)

    return f"""
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Relatório visual - Tele Severino</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      padding: 24px;
      background: #f6f7fb;
      color: #111827;
    }}
    h1, h2 {{
      margin-bottom: 8px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 18px 0 32px;
      background: #fff;
      border-radius: 12px;
      overflow: hidden;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid #e5e7eb;
      font-size: 13px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #111827;
      color: #fff;
    }}
    code {{
      background: #eef2ff;
      padding: 2px 6px;
      border-radius: 6px;
    }}
  </style>
</head>
<body>
  <h1>Relatório visual - Tele Severino</h1>
  <p>Validação automática de fontes, textos, títulos, subtítulos e diferença entre light/dark.</p>

  <h2>Páginas validadas</h2>
  <table>
    <thead>
      <tr>
        <th>Perfil</th>
        <th>Rota</th>
        <th>Elementos light</th>
        <th>Elementos dark</th>
      </tr>
    </thead>
    <tbody>
      {"".join(paginas)}
    </tbody>
  </table>

  <h2>Problemas encontrados</h2>
  <table>
    <thead>
      <tr>
        <th>Tipo</th>
        <th>Perfil</th>
        <th>Rota</th>
        <th>Tema</th>
        <th>Categoria</th>
        <th>Fonte light/atual</th>
        <th>Fonte dark</th>
        <th>Texto</th>
        <th>Mensagem</th>
      </tr>
    </thead>
    <tbody>
      {"".join(linhas)}
    </tbody>
  </table>
</body>
</html>
"""


if __name__ == "__main__":
    main()
