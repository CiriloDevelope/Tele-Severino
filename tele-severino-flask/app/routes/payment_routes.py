from flask import Blueprint, render_template
from app.services.specialist_service import get_specialist_profile

payment_bp = Blueprint("payment", __name__)


@payment_bp.route("/pagamento/<int:specialist_id>")
def pagamento(specialist_id):
    specialist = get_specialist_profile(specialist_id)

    # Futuro PostgreSQL:
    # Buscar chamada encerrada.
    # Calcular total.
    # Criar pagamento.
    # Atualizar status para pago.

    return render_template("pagamento.html", specialist=specialist)
