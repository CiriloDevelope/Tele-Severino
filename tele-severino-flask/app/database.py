# ============================================================
# PONTO CENTRAL DE CONEXÃO COM BANCO POSTGRESQL
# ============================================================
# Futuramente este arquivo deve concentrar a conexão com o banco.
#
# Exemplo com SQLAlchemy:
#
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()
#
# Depois, no app/__init__.py:
#
# db.init_app(app)
#
# Por enquanto o projeto continua usando dados mockados.
# ============================================================


def get_db_connection():
    # Futuro exemplo com psycopg2:
    #
    # import psycopg2
    # from flask import current_app
    # return psycopg2.connect(current_app.config["DATABASE_URL"])
    #
    return None
