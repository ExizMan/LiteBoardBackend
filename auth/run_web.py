import os

from fastapi import FastAPI
import uvicorn

from auth.src.routers import router as router_auth

from fastapi import Response


app = FastAPI()


@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = Response()

    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

    return response


app.include_router(router_auth)




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    #для запуска через консоль с перезагрузкой сервера на том же порту и хосте: uvicorn run_web:app --reload --host 0.0.0.0 --port 8000