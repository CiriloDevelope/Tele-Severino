import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # ============================================================
    # INTEGRAÇÃO FUTURA COM MYSQL
    # ============================================================
    # Quando for integrar com banco real, criar um arquivo .env:
    #
    # MYSQL_DATABASE_URL=mysql://usuario:senha@localhost:3306/tele_severino
    #
    # Ou usar variáveis separadas:
    #
    # MYSQL_HOST=localhost
    # MYSQL_PORT=3306
    # MYSQL_USER=usuario
    # MYSQL_PASSWORD=senha
    # MYSQL_DATABASE=tele_severino
    # ============================================================

    MYSQL_DATABASE_URL = os.getenv(
        "MYSQL_DATABASE_URL",
        "mysql://usuario:senha@localhost:3306/tele_severino"
    )

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "usuario")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "senha")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "tele_severino")
