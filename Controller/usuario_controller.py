from fastapi import APIRouter
from Model.usuario_model import cadastrar_usuario

router = APIRouter()

@router.post("/usuarios")
def criar_usuario(dados: dict = None):
    nome = "Cicero Jegue" #dados.get("nome")
    email = "ciceroExplodeBunda@gmail.com" #dados.get("email")
    senha = "1234"  #dados.get("senha")
    tipo = "cliente" #dados.get("tipo")

    resultado = cadastrar_usuario(nome, email, senha, tipo)

    return resultado