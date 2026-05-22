from flask import Blueprint, render_template
from app.services.specialist_service import get_specialist_profile

call_bp = Blueprint("call", __name__)


@call_bp.route("/chamada/<int:specialist_id>")
def chamada(specialist_id):
    specialist = get_specialist_profile(specialist_id)

    # Futuro PostgreSQL:
    # INSERT INTO calls (user_id, specialist_id, started_at, status)
    # VALUES (..., ..., NOW(), 'in_progress');

    return render_template("chamada.html", specialist=specialist)
