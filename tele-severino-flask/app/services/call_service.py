from app.repositories.call_repository import create_call, finish_call, get_call_by_id


def start_call(user_id, specialist_id):
    # Regra futura:
    # - Validar se usuário está logado.
    # - Validar se especialista está online.
    # - Validar se existe forma de pagamento ativa.
    return create_call(user_id, specialist_id)


def end_call(call_id, total_seconds, price_per_minute):
    # O cálculo final precisa ficar no backend para evitar manipulação pelo frontend.
    total_value = (total_seconds / 60) * float(price_per_minute)
    return finish_call(call_id, total_seconds, total_value)


def get_call_summary(call_id):
    return get_call_by_id(call_id)
