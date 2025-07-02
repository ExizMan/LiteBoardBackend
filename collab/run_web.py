import os

from fastapi import FastAPI
import uvicorn

from collab.src.routers import router as router_auth
from fastapi.middleware.cors import CORSMiddleware
from collab.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_auth)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    #для запуска через консоль с перезагрузкой сервера на том же порту и хосте: uvicorn run_web:app --reload --host 0.0.0.0 --port 8000