from fastapi import APIRouter
from pydantic import BaseModel
from Model.ia_model import gerar_resposta_ia

router = APIRouter()

class PerguntaIA(BaseModel):
    pergunta: str
    

@router.post("/ia")
def resposta_ia(dados: PerguntaIA):
    return gerar_resposta_ia(dados.pergunta)