from fastapi import APIRouter
from Model.usuario_model import cadastrar_usuario
from Model.usuario_model import consultar_usuarios

router = APIRouter()

@router.post("/usuarios")
def criar_usuario(dados: dict = None):
    nome = "Cicero" #dados.get("nome")
    email = "cicero@gmail.com" #dados.get("email")
    senha = "1234"  #dados.get("senha")
    tipo = "cliente" #dados.get("tipo")

    resultado = cadastrar_usuario(nome, email, senha, tipo)

    return resultado

@router.post("/usuarios/login")
def consulta_usuario(email: str):
    usuario = consultar_usuarios(email)

    return {"mensagem": f"Dados retornado {usuario}"}


consulta_usuario("cicero@gmail.com")