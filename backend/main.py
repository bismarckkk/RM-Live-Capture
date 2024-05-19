import re
import secrets
import base64
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Path, Request
from fastapi.responses import JSONResponse

import config
from range_response import RangeResponse
from manager import Manager, get_live_info, LiveStreamReq
from video import filter_video_list, VideoFilterProps, get_video_info, convert_to_mp4, delete_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await manager.close()


app = FastAPI(lifespan=lifespan)
manager = Manager()
path_regex = re.compile(r"^\d+_\d+_\d+_\d+\.m3u8$")
path_f_regex = re.compile(r"^\d+_\d+_\d+_\d+-\d+\.ts$")


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


@app.post("/api/video/list")
async def get_video(props: VideoFilterProps):
    return filter_video_list(**props.dict())


@app.get("/api/video/convert/{file_name}")
async def convert_video(file_name: str = Path()):
    if not path_regex.match(file_name):
        return JSONResponse({"code": -1, "msg": "Illegal file name"}, 400)
    if not (config.save_dir / file_name).exists():
        return JSONResponse({"code": 2, "msg": "M3U8 file not exist."}, 404)
    mp4 = config.mp4_dir / f"{get_video_info(file_name).title}.mp4"
    if not mp4.exists():
        await convert_to_mp4(get_video_info(file_name))
    return {"code": 0}


@app.get("/api/video/delete/{file_name}")
async def delete_video(file_name: str = Path()):
    if not path_regex.match(file_name):
        return JSONResponse({"code": -1, "msg": "Illegal file name"}, 400)
    if not (config.save_dir / file_name).exists():
        return JSONResponse({"code": 2, "msg": "M3U8 file not exist."}, 404)
    delete_file(get_video_info(file_name))
    return JSONResponse({"code": 0}, 200)


@app.get("/api/video/file/{file_name}")
async def get_video_file(request: Request, file_name: str = Path()):
    if not (path_regex.match(file_name) or path_f_regex.match(file_name)):
        return JSONResponse({"code": -1, "msg": "Illegal file name"}, 400)
    if not (config.save_dir / file_name).exists():
        return JSONResponse({"code": 2, "msg": "M3U8 file not exist."}, 404)
    mime = "video/MP2T" if path_f_regex.match(file_name) else "application/x-mpegURL"
    return RangeResponse(request, str(config.save_dir / file_name), mime)


@app.get("/api/video/download/{file_name}")
async def download_video(request: Request, file_name: str = Path()):
    if not path_regex.match(file_name):
        return JSONResponse({"code": -1, "msg": "Illegal file name"}, 400)
    if not (config.save_dir / file_name).exists():
        return JSONResponse({"code": 2, "msg": "M3U8 file not exist."}, 404)
    mp4 = config.mp4_dir / f"{get_video_info(file_name).title}.mp4"
    if not mp4.exists():
        return JSONResponse({"code": 1, "msg": "MP4 file not created"}, 404)
    return RangeResponse(request, str(mp4), "video/mp4")


if __name__ == '__main__':
    import uvicorn
    asyncio.run(manager.init())
    uvicorn.run(app, host="0.0.0.0", port=config.port)

