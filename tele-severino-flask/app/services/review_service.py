from app.repositories.review_repository import create_review


def save_review(user_id, specialist_id, rating, comment, call_id=1):
    # Regra futura:
    # - Permitir avaliação apenas após chamada finalizada.
    # - Permitir avaliação apenas após pagamento confirmado.
    return create_review(user_id, specialist_id, call_id, rating, comment)
