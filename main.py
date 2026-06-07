from fastapi import FastAPI
from Controller.usuario_controller import router as usuario_router

app = FastAPI()

app.include_router(usuario_router)