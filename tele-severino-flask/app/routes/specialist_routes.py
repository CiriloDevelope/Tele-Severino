from flask import Blueprint, render_template, request
from app.services.specialist_service import get_specialists_page, get_specialist_profile

specialist_bp = Blueprint("specialist", __name__)


@specialist_bp.route("/especialistas")
def especialistas():
    category = request.args.get("categoria")
    title, subtitle, specialists = get_specialists_page(category)
    return render_template(
        "especialistas.html",
        specialists=specialists,
        title=title,
        subtitle=subtitle
    )


@specialist_bp.route("/especialista/<int:specialist_id>")
def especialista(specialist_id):
    specialist = get_specialist_profile(specialist_id)
    return render_template("perfil.html", specialist=specialist)
