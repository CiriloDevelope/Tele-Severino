from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from Model.usuario_model import cadastrar_usuario
from Model.usuario_model import consultar_usuarios
from Model.usuario_model import senha_hash
from Model.usuario_model import atualizar_dados
from Model.usuario_model import excluir_usuario

router = APIRouter()

class UsuarioCadastro(BaseModel):
    nome:str
    email:str
    senha:str
    tipo:str

class UsuarioLogin(BaseModel):
    email: str
    senha: str

@router.post("/usuarios")
def criar_usuario(dados:UsuarioCadastro):
    
    resultado = cadastrar_usuario(dados.nome, dados.email, dados.senha, dados.tipo)

    return resultado

@router.post("/login")
def validar_login(dados:UsuarioLogin):

    usuario = consultar_usuarios(dados.email)

    if usuario is None:
        return{"erro": "Usuario nao encontrado"}
    
    senha_banco = usuario[3]
    email_banco = usuario[2]

    if email_banco == dados.email and senha_banco == senha_hash(dados.senha):
        return{"mensagem": "Login confirmado"}

    return{"erro": "Login ou senha invalidos!"}


@router.put("/usuario/{id}")
def atualizar_usuario(id: int, dados: UsuarioCadastro):

    resultado = atualizar_dados(id, dados.nome, dados.email, dados.senha, dados.tipo)

    if "erro" in resultado:
        raise HTTPException(status_code=404, detail=resultado["erro"])

    return {"mensagem": "Usuário atualizado com sucesso!"}


@router.delete("/delete_usuario/{id}")
def deletar_usuario(id: int):

    resultado = excluir_usuario(id)

    if "erro" in resultado:
        raise HTTPException(status_code=404, detail=resultado["erro"])
        

    return resultado

    



#consulta_usuario("cicero@gmail.com")