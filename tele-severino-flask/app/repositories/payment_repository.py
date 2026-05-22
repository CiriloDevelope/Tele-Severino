# ============================================================
# REPOSITORY DE PAGAMENTOS
# ============================================================
# Responsável por criar e atualizar pagamentos.
# ============================================================


def create_payment(user_id, specialist_id, call_id, amount, method):
    # Futuro PostgreSQL:
    #
    # INSERT INTO payments (user_id, specialist_id, call_id, amount, method, status, created_at)
    # VALUES (%s, %s, %s, %s, %s, 'pending', NOW())
    # RETURNING id;
    #
    return {
        "id": 1,
        "user_id": user_id,
        "specialist_id": specialist_id,
        "call_id": call_id,
        "amount": amount,
        "method": method,
        "status": "pending"
    }


def confirm_payment(payment_id):
    # Futuro PostgreSQL:
    #
    # UPDATE payments
    # SET status = 'paid',
    #     paid_at = NOW()
    # WHERE id = %s;
    #
    return True
