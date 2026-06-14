from fastapi import FastAPI
from Controller.usuario_controller import router as usuario_router
from Controller.especialista_controller import router as especialista_router
from Controller.ia_controller import router as ia_router

app = FastAPI()

app.include_router(usuario_router)
app.include_router(especialista_router)
app.include_router(ia_router)