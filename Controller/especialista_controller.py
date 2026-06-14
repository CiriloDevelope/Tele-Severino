from fastapi import APIRouter
from Model.database import conectar_banco
from Model.especialista_model import EspecialistaCreate, EspecialistaUpdate

router = APIRouter(
    prefix="/especialistas",
    tags=["Especialistas"]
)

# 1. CADASTRAR ESPECIALISTA
@router.post("/")
def cadastrar_especialista(dados: EspecialistaCreate):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        INSERT INTO especialistas (id_especialista, especialidade, valor_minuto)
        VALUES (%s, %s, %s)
        """
        valores = (dados.id_especialista, dados.especialidade, dados.valor_minuto)

        cursor.execute(sql, valores)
        conexao.commit()

        return {"mensagem": "Especialista cadastrado com sucesso"}

    except Exception as erro:
        return {"erro": str(erro)}

    finally:
        if conexao:
            conexao.close()

# 2. CONSULTAR TODOS OS ESPECIALISTAS
@router.get("/")
def consultar_todos_especialistas():
    conexao = None
    try:
        conexao = conectar_banco()
        # dictionary=True facilita o retorno no formato JSON para o FastAPI
        cursor = conexao.cursor(dictionary=True) 

        sql = "SELECT id_especialista, especialidade, valor_minuto FROM especialistas"
        cursor.execute(sql)

        especialistas = cursor.fetchall()

        return especialistas
    
    except Exception as erro:
        return {"erro": str(erro)}
        
    finally:
        if conexao:
            conexao.close()

# 3. CONSULTAR UM ESPECIALISTA POR ID
@router.get("/{id_especialista}")
def consultar_especialista(id_especialista: int):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        sql = "SELECT id_especialista, especialidade, valor_minuto FROM especialistas WHERE id_especialista = %s"
        cursor.execute(sql, (id_especialista,))

        especialista = cursor.fetchone()
        
        if not especialista:
            return {"erro": "Especialista não encontrado"}

        return especialista
    
    except Exception as erro:
        return {"erro": str(erro)}
        
    finally:
        if conexao:
            conexao.close()

# 4. ATUALIZAR DADOS DO ESPECIALISTA
@router.put("/{id_especialista}")
def atualizar_dados(id_especialista: int, dados: EspecialistaUpdate):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
        UPDATE especialistas SET especialidade = %s, valor_minuto = %s WHERE id_especialista = %s;
        """
        valores = (dados.especialidade, dados.valor_minuto, id_especialista)
        
        cursor.execute(sql, valores)
        conexao.commit()  

        if cursor.rowcount == 0:
            return {"erro": "Especialista não encontrado para o ID informado ou dados iguais"}

        return {"sucesso": "Dados atualizados com sucesso"}

    except Exception as erro:
        return {"erro": str(erro)}
        
    finally:
        if conexao:
            conexao.close()

# 5. EXCLUIR ESPECIALISTA
@router.delete("/{id_especialista}")
def excluir_especialista(id_especialista: int):
    conexao = None
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
            DELETE FROM especialistas WHERE id_especialista = %s
        """
        valores = (id_especialista,)

        cursor.execute(sql, valores)
        conexao.commit()

        if cursor.rowcount == 0:
            return {"erro": "Especialista não encontrado para o ID informado"}

        return {"sucesso": "Especialista DELETADO!"}

    except Exception as erro:
        return {"erro": str(erro)}
        
    finally:
        if conexao:
            conexao.close()