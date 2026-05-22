def login_user(email, password):
    # Futuro backend + PostgreSQL:
    # 1. Buscar usuário pelo email.
    # 2. Validar senha usando hash.
    # 3. Criar sessão/JWT.
    return {"email": email}


def register_user(name, email, password, account_type):
    # Futuro backend + PostgreSQL:
    # INSERT INTO users (name, email, password_hash, account_type, created_at)
    # VALUES (...);
    #
    # Importante: nunca salvar senha pura.
    return {
        "name": name,
        "email": email,
        "account_type": account_type
    }
