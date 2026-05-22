from flask import Blueprint, render_template, request, redirect, url_for
from app.services.specialist_service import get_specialist_profile
from app.services.review_service import save_review

review_bp = Blueprint("review", __name__)


@review_bp.route("/avaliacao/<int:specialist_id>", methods=["GET", "POST"])
def avaliacao(specialist_id):
    specialist = get_specialist_profile(specialist_id)

    if request.method == "POST":
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        # Futuro PostgreSQL:
        # user_id virá da sessão do usuário logado.
        save_review(user_id=1, specialist_id=specialist_id, rating=rating, comment=comment)

        return redirect(url_for("main.home"))

    return render_template("avaliacao.html", specialist=specialist)
