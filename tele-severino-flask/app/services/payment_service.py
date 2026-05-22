from app.repositories.payment_repository import create_payment, confirm_payment


def create_consultation_payment(user_id, specialist_id, call_id, amount, method):
    # Regra futura:
    # - Validar chamada finalizada.
    # - Validar valor calculado pelo backend.
    # - Integrar com gateway de pagamento.
    return create_payment(user_id, specialist_id, call_id, amount, method)


def approve_payment(payment_id):
    return confirm_payment(payment_id)
