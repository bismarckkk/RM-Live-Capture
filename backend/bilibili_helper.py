from typing import Union, List
import base64

from bilibili_api import Credential
from bilibili_api import video_uploader
from bilibili_api.user import get_self_info
from bilibili_api.login_func import get_qrcode, check_qrcode_events, QrCodeLoginEvents
from pydantic import BaseModel

import config
from logger import getLogger

logger = getLogger(f"Uploader", "INFO")


class CookieInfo(BaseModel):
    sessdata: Union[str, None] = None
    dedUserIf: Union[str, None] = None
    bili_jct: Union[str, None] = None
    buvid3: Union[str, None] = None
    ac_time_value: Union[str, None] = None

    def to_credential(self):
        return Credential.from_cookies(self.dict())

    def save_cookie(self):
        with open('cookie.json', 'w') as f:
            f.write(self.json())


def load_cookie() -> CookieInfo:
    with open('cookie.json', 'r') as f:
        data = f.read()
    return CookieInfo.parse_raw(data)


async def login():
    qr, key = get_qrcode()
    qr64 = 'data:image/' + qr.imageType + ';base64,' + base64.b64encode(qr.content).decode()
    return qr64, key


def check_qrcode_events(key: str):
    status, cred = check_qrcode_events(key)
    if status == QrCodeLoginEvents.DONE:
        cookie = CookieInfo(**cred.get_cookies())
        cookie.save_cookie()
    return status


async def get_username():
    try:
        cookie = load_cookie()
    except:
        return '请先登录'
    cred = cookie.to_credential()
    info = await get_self_info(cred)
    return info['data']['name']


async def upload_video(title: str, videos: List[str]):
    cookie = load_cookie()
    cred = cookie.to_credential()
    vu_meta = video_uploader.VideoMeta(
        tid=233,
        title=title,
        desc=title,
        cover='cover.png',
        tags=['RoboMaster'],
    )
    pages = [
        video_uploader.VideoUploaderPage(path=str(config.mp4_dir / f'{video}.mp4'), title=video) for video in videos
    ]
    uploader = video_uploader.VideoUploader(pages, vu_meta, cred)

    @uploader.on("__ALL__")
    async def ev(data):
        logger.info(f"Event: {data}")

    await uploader.start()
