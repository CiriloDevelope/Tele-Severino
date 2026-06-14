from pydantic import BaseModel

class EspecialistaCreate(BaseModel):
    id_especialista: int
    especialidade: str
    valor_minuto: float

class EspecialistaUpdate(BaseModel):
    especialidade: str
    valor_minuto: float