from Model.database import conectar_banco

def cadastrar_usuario(nome, email, senha, tipo):
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (%s, %s, %s, %s)
        """

        valores = (nome, email, senha, tipo)

        cursor.execute(sql, valores)
        conexao.commit()

        return {"mensagem": "Usuário cadastrado com sucesso"}

    except Exception as erro:
        return {"erro": str(erro)}

    finally:
        if conexao:
            conexao.close()