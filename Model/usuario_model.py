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

def atualizar_dados(id, nome, email, senha, tipo):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()  #

        sql = """
        UPDATE usuarios SET nome = %s, email = %s, senha = %s, tipo = %s WHERE id_usuario = %s;
        """
        
        # CORRIGIDO: Passando os valores com a senha já criptografada
        valores = (nome, email, senha_hash(senha), tipo, id)
        
        cursor.execute(sql, valores)
        conexao.commit()  

        #Rowcount me fala quantas linhas foram afetadas, assim fica mais facil de debugar.
        if cursor.rowcount == 0:
            return {"erro": "Usuario nao encontrado para o ID informado"}

        return {"sucesso": "Dados atualizados com sucesso"}

    except Exception as erro:
        return {"erro": str(erro)}
        
    finally:
        if conexao:
            conexao.close()

def excluir_usuario(id):
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
            DELETE FROM usuarios WHERE id_usuario = %s
        """

        valores = (id,)

        cursor.execute(sql, valores)
        conexao.commit()

        if cursor.rowcount == 0:
            return {"erro": "Usuario nao encontrado para o ID informado"}

        return {"sucesso": "Usuario DELETADO!"}

    except Exception as erro:
        return {"erro": str(erro)}
        
    finally:
        if conexao:
            conexao.close()
