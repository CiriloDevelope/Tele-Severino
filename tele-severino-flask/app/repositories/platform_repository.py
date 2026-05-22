# ============================================================
# REPOSITORY DE PERSONALIZAÇÃO DA MARCA
# ============================================================
# Responsável por buscar e salvar nome, cor e logo da plataforma.
# ============================================================


def get_platform_settings():
    # Futuro PostgreSQL:
    #
    # SELECT *
    # FROM platform_settings
    # LIMIT 1;
    #
    return {
        "platform_name": "Tele Severino",
        "primary_color": "#F97316",
        "logo_url": None
    }


def update_platform_settings(platform_name, primary_color, logo_url=None):
    # Futuro PostgreSQL:
    #
    # UPDATE platform_settings
    # SET platform_name = %s,
    #     primary_color = %s,
    #     logo_url = %s,
    #     updated_at = NOW()
    # WHERE id = 1;
    #
    return True
