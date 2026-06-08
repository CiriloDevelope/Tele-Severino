from Model.database import conectar_banco
import hashlib

def senha_hash(senha):
    texto = str(senha).encode()

    hash_objeto = hashlib.sha3_256(texto)

    codigo_hash = hash_objeto.hexdigest()

    return codigo_hash

def cadastrar_usuario(nome, email, senha, tipo):
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO usuarios (nome, email, senha, tipo)
        VALUES (%s, %s, %s, %s)
        """

        valores = (nome, email, senha_hash(senha), tipo)

        cursor.execute(sql, valores)
        conexao.commit()

        return {"mensagem": "Usuário cadastrado com sucesso"}

    except Exception as erro:
        return {"erro": str(erro)}

    finally:
        if conexao:
            conexao.close()

def consultar_usuarios(email):
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        SELECT id_usuario, nome, email, senha, tipo FROM usuarios WHERE email = %s
        """
        cursor.execute(sql,(email,))

        usuario = cursor.fetchone()

        return usuario
    
    except Exception as erro:
        return {"erro": str(erro)}
        
    finally:
        if conexao:
            conexao.close()
