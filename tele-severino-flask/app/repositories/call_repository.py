# ============================================================
# REPOSITORY DE CHAMADAS
# ============================================================
# Responsável por salvar início, fim, tempo e valor das chamadas.
# ============================================================


def create_call(user_id, specialist_id):
    # Futuro PostgreSQL:
    #
    # INSERT INTO calls (user_id, specialist_id, started_at, status)
    # VALUES (%s, %s, NOW(), 'in_progress')
    # RETURNING id;
    #
    return {
        "id": 1,
        "user_id": user_id,
        "specialist_id": specialist_id,
        "status": "in_progress"
    }


def finish_call(call_id, total_seconds, total_value):
    # Futuro PostgreSQL:
    #
    # UPDATE calls
    # SET ended_at = NOW(),
    #     total_seconds = %s,
    #     total_value = %s,
    #     status = 'finished'
    # WHERE id = %s;
    #
    return True


def get_call_by_id(call_id):
    # Futuro PostgreSQL:
    #
    # SELECT *
    # FROM calls
    # WHERE id = %s;
    #
    return {
        "id": call_id,
        "total_seconds": 15,
        "total_value": 1.25,
        "status": "finished"
    }
