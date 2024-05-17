import secrets
import base64
import asyncio

from fastapi import FastAPI, Query, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

import config
from manager import Manager, get_live_info, LiveStreamReq

app = FastAPI()
manager = Manager()


def check_permission(info):
    info = info.replace("Basic ", "")
    current_username_bytes, current_password_bytes = base64.b64decode(info).decode().split(':', 1)
    is_correct_username = secrets.compare_digest(current_username_bytes.encode(), config.username)
    is_correct_password = secrets.compare_digest(current_password_bytes.encode(), config.password)
    return is_correct_username and is_correct_password


@app.middleware("http")
async def check_auth(request: Request, call_next):
    if config.basic_security:
        if "Authorization" not in request.headers:
            return JSONResponse(None, 401, {"WWW-Authenticate": "Basic"})
        if not check_permission(request.headers["Authorization"]):
            return JSONResponse(None, 401, {"WWW-Authenticate": "Basic"})
    return await call_next(request)


@app.get("/api/manager")
async def get_manager():
    return manager.get()


@app.get("/api/manager/live")
async def get_manager():
    return await get_live_info()


@app.get("/api/manager/delete")
async def delete_manager(role: str):
    await manager.delete_req(role)
    return manager.get()


@app.get("/api/manager/add")
async def add_manager(role: str, quality: str):
    await manager.add_req(LiveStreamReq(role=role, quality=quality))
    return manager.get()


@app.get("/api/manager/update")
async def update_manager(role: str, quality: str):
    await manager.update_req(role, quality)
    return manager.get()


@app.on_event("shutdown")
async def on_shutdown():
    await manager.close()


if __name__ == '__main__':
    import uvicorn
    asyncio.run(manager.init())
    uvicorn.run(app, host="0.0.0.0", port=config.port)

