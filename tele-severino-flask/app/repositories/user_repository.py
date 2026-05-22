# ============================================================
# REPOSITORY DE USUÁRIOS
# ============================================================
# Este arquivo será responsável por buscar e salvar usuários no PostgreSQL.
# Por enquanto está mockado para manter o protótipo funcionando.
# ============================================================


def find_user_by_email(email):
    # Futuro PostgreSQL:
    #
    # SELECT *
    # FROM users
    # WHERE email = %s;
    #
    return None


def create_user(name, email, password_hash, account_type):
    # Futuro PostgreSQL:
    #
    # INSERT INTO users (name, email, password_hash, account_type, created_at)
    # VALUES (%s, %s, %s, %s, NOW())
    # RETURNING id;
    #
    return {
        "id": 1,
        "name": name,
        "email": email,
        "account_type": account_type
    }
