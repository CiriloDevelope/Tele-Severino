from app.repositories.platform_repository import (
    get_platform_settings,
    update_platform_settings,
)


def get_settings():
    return get_platform_settings()


def save_settings(platform_name, primary_color, logo_url=None):
    return update_platform_settings(platform_name, primary_color, logo_url)
