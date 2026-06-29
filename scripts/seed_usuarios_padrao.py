import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from Model.database import conectar_banco
from Model.usuario_model import senha_hash


SENHA_PADRAO = "123456"



def garantir_usuario(cursor, nome, email, senha, tipo):
    senha_criptografada = senha_hash(senha)

    cursor.execute(
        "SELECT id_usuario FROM usuarios WHERE email = %s",
        (email,),
    )
    existente = cursor.fetchone()

    if existente:
        id_usuario = existente[0] if not isinstance(existente, dict) else existente["id_usuario"]
        cursor.execute(
            """
            UPDATE usuarios
               SET nome = %s,
                   senha = %s,
                   tipo = %s
             WHERE id_usuario = %s
            """,
            (nome, senha_criptografada, tipo, id_usuario),
        )
        print(f"Atualizado: {email}")
        return id_usuario

    cursor.execute(
        """
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (%s, %s, %s, %s)
        """,
        (nome, email, senha_criptografada, tipo),
    )
    id_usuario = cursor.lastrowid
    print(f"Criado: {email}")
    return id_usuario


def garantir_especialista(cursor, id_usuario, especialidade, valor_minuto):
    cursor.execute(
        "SELECT id_especialista FROM especialistas WHERE id_especialista = %s",
        (id_usuario,),
    )
    existente = cursor.fetchone()

    if existente:
        cursor.execute(
            """
            UPDATE especialistas
               SET especialidade = %s,
                   valor_minuto = %s
             WHERE id_especialista = %s
            """,
            (especialidade, valor_minuto, id_usuario),
        )
        print(f"Especialista atualizado: {id_usuario}")
        return

    cursor.execute(
        """
        INSERT INTO especialistas (id_especialista, especialidade, valor_minuto)
        VALUES (%s, %s, %s)
        """,
        (id_usuario, especialidade, valor_minuto),
    )
    print(f"Especialista criado: {id_usuario}")


def main():
    conexao = conectar_banco()

    if not conexao:
        raise RuntimeError("Não foi possível conectar no banco.")

    cursor = conexao.cursor()

    usuarios = [
        ("Super Admin", "super.admin@teste.com", SENHA_PADRAO, "SUPER_ADMIN"),
        ("Admin Tele Severino", "admin.tele@teste.com", SENHA_PADRAO, "ADMIN"),
        ("Cliente Navegador", "cliente.navegador@teste.com", SENHA_PADRAO, "CLIENTE"),
        ("Especialista Navegador", "especialista.navegador@teste.com", SENHA_PADRAO, "ESPECIALISTA"),
    ]

    ids = {}

    for nome, email, senha, tipo in usuarios:
        ids[email] = garantir_usuario(cursor, nome, email, senha, tipo)

    garantir_especialista(
        cursor,
        ids["especialista.navegador@teste.com"],
        "Elétrica Residencial",
        4.50,
    )

    conexao.commit()
    cursor.close()
    conexao.close()

    print("\nUsuários padrão prontos:")
    for _, email, _, tipo in usuarios:
        print(f"- {tipo}: {email} / {SENHA_PADRAO}")


if __name__ == "__main__":
    main()
