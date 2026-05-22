from app.data import SPECIALISTS


def list_specialists():
    # Futuro PostgreSQL:
    # SELECT * FROM specialists WHERE is_online = true ORDER BY rating DESC;
    return SPECIALISTS


def list_home_specialists():
    # Futuro PostgreSQL:
    # SELECT * FROM specialists WHERE is_online = true LIMIT 3;
    return SPECIALISTS[:3]


def list_specialists_by_category(category_slug):
    # Futuro PostgreSQL:
    # SELECT * FROM specialists WHERE category_slug = %s AND is_online = true;
    return [item for item in SPECIALISTS if item["category"] == category_slug]


def get_specialist_by_id(specialist_id):
    # Futuro PostgreSQL:
    # SELECT * FROM specialists WHERE id = %s;
    return next((item for item in SPECIALISTS if item["id"] == specialist_id), SPECIALISTS[0])
