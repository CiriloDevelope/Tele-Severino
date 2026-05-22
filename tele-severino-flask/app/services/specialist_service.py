from app.repositories.specialist_repository import (
    list_specialists,
    list_home_specialists,
    list_specialists_by_category,
    get_specialist_by_id,
)
from app.repositories.category_repository import get_category_name


def get_home_specialists():
    return list_home_specialists()


def get_specialists_page(category=None):
    if category:
        specialists = list_specialists_by_category(category)
        title = f"Especialistas em {get_category_name(category)}"
        subtitle = f"{len(specialists)} profissional online" if len(specialists) == 1 else f"{len(specialists)} profissionais online"
        return title, subtitle, specialists

    return "Especialistas disponíveis", "14 profissionais online", list_specialists()


def get_specialist_profile(specialist_id):
    return get_specialist_by_id(specialist_id)
