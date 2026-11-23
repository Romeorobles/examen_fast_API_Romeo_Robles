from fastapi import FastAPI

from app.planes import router as planes_router

app = FastAPI(title="Gimnasio — Planes de Membresía")

app.include_router(planes_router)
