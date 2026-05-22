# ============================================================
# REPOSITORY DE AVALIAÇÕES
# ============================================================
# Responsável por salvar avaliações dos especialistas.
# ============================================================


def create_review(user_id, specialist_id, call_id, rating, comment):
    # Futuro PostgreSQL:
    #
    # INSERT INTO reviews (user_id, specialist_id, call_id, rating, comment, created_at)
    # VALUES (%s, %s, %s, %s, %s, NOW());
    #
    return {
        "user_id": user_id,
        "specialist_id": specialist_id,
        "call_id": call_id,
        "rating": rating,
        "comment": comment
    }


def list_reviews_by_specialist(specialist_id):
    # Futuro PostgreSQL:
    #
    # SELECT *
    # FROM reviews
    # WHERE specialist_id = %s
    # ORDER BY created_at DESC;
    #
    return []
