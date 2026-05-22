from app.data import CATEGORIES


def list_categories():
    # Futuro PostgreSQL:
    # SELECT slug, name, icon, tone FROM categories ORDER BY name;
    return CATEGORIES


def get_category_name(slug):
    # Futuro PostgreSQL:
    # SELECT name FROM categories WHERE slug = %s;
    category = next((item for item in CATEGORIES if item["slug"] == slug), None)
    return category["name"] if category else "Especialistas"
