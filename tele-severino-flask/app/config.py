import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # ============================================================
    # INTEGRAÇÃO FUTURA COM POSTGRESQL
    # ============================================================
    # Quando for integrar com banco real, criar um arquivo .env:
    #
    # DATABASE_URL=postgresql://usuario:senha@localhost:5432/tele_severino
    #
    # Esse valor será usado pelo SQLAlchemy ou psycopg2.
    # ============================================================
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://usuario:senha@localhost:5432/tele_severino"
    )
