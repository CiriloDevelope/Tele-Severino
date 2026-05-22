from flask import Blueprint, render_template

brand_bp = Blueprint("brand", __name__)


@brand_bp.route("/personalizacao")
def personalizacao():
    # Futuro PostgreSQL:
    # Buscar/salvar nome, logo e cor principal em platform_settings.
    return render_template("personalizacao.html")
