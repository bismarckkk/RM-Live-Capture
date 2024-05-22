from typing import List, Dict, Union
import json
import asyncio

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from pydantic import BaseModel

import config
from downloader import Downloader, RoundInfo
from logger import getLogger


class LiveInfo(BaseModel):
    live: bool
    streams: Dict[str, Dict[str, str]]


class LiveStreamReq(BaseModel):
    quality: str
    role: str


class DownloaderInfo(BaseModel):
    name: str
    status: bool
    error_count: int
    quality: str = "None"
    recorded: float = 0


class ManagerInfo(BaseModel):
    round_info: RoundInfo
    downloaders: List[DownloaderInfo]


async def get_round_info() -> RoundInfo:
    async with aiohttp.ClientSession(headers=config.oss_headers) as session:
        async with session.get(config.round_info_url) as response:
            _data = await response.json()
            info = RoundInfo(red="Null", blue="Null", round=0, id=0, status="IDLE")
            for data in _data:
                data = data['currentMatch']
                if data is None:
                    continue
                info = RoundInfo(**{
                    "red": data['redSide']['player']['team']['collegeName'],
                    "blue": data['blueSide']['player']['team']['collegeName'],
                    "round": data['round'],
                    "id": data['id'],
                    "status": data['status']
                })
                break
            return info


def live_string_to_dict(live_string: List) -> Dict[str, str]:
    res = {}
    for stream in live_string:
        res[stream['label']] = stream['src']
    return res


async def get_live_info() -> LiveInfo:
    async with aiohttp.ClientSession(headers=config.oss_headers) as session:
        async with session.get(config.live_info_url) as response:
            data = json.loads(await response.text())['eventData']
            info = {
                "live": False,
                "streams": {}
            }
            ok = False
            for live_info in data:
                if live_info['liveState'] != 1 or live_info['matchState'] != 1:
                    continue
                ok = True
                info['live'] = True
                mainStream = live_string_to_dict(live_info['zoneLiveString'])
                if mainStream:
                    info['streams']['主视角'] = mainStream
                for fpv in live_info['fpvData']:
                    stream = live_string_to_dict(fpv['sources'])
                    if stream:
                        info['streams'][fpv['role']] = stream
            if not ok:
                live_info = data[0]
                mainStream = live_string_to_dict(live_info['zoneLiveString'])
                if mainStream:
                    info['streams']['主视角'] = mainStream
                for fpv in live_info['fpvData']:
                    stream = live_string_to_dict(fpv['sources'])
                    if stream:
                        info['streams'][fpv['role']] = stream
            return LiveInfo(**info)


class Manager:
    def __init__(self, reqs: List[LiveStreamReq] = None):
        if reqs is None:
            reqs = []
            if config.reqs_json.exists():
                with open(config.reqs_json, "r") as f:
                    reqs = [LiveStreamReq(**it) for it in json.load(f)]
        self.downloaders: Dict[str, Union[Downloader, None]] = {}
        self.scheduler = AsyncIOScheduler()
        self.reqs = reqs
        self.round: Union[RoundInfo, None] = None
        self.status = "IDLE"
        self.job: Union[Job, None] = None
        self.logger = getLogger("Manager", "INFO")

    async def init(self):
        self.scheduler.start()
        live_info = await get_live_info()
        for req in self.reqs:
            stream = live_info.streams.get(req.role, {}).get(req.quality)
            if stream is None:
                self.downloaders[req.role] = None
            else:
                self.downloaders[req.role] = Downloader(req.role, stream, self.scheduler)
                self.logger.info(f"Add {req.role} to downloaders")
        self.job = self.scheduler.add_job(self.scan, "interval", seconds=10)
        await self.scan()

    async def scan(self):
        self.logger.info("Scanning...")
        live_info = await get_live_info()
        for req in self.reqs:
            stream = live_info.streams.get(req.role, {}).get(req.quality)
            if stream is not None:
                if self.downloaders.get(req.role) is None:
                    self.downloaders[req.role] = Downloader(req.role, stream, self.scheduler)
                else:
                    self.downloaders[req.role].url = stream
        if not live_info.live:
            if self.status == 'STARTED':
                for downloader in self.downloaders.values():
                    if downloader is not None:
                        await downloader.end()
                self.status = "IDLE"
                self.round = await get_round_info()
            self.job.reschedule(trigger="interval", seconds=120)
        else:
            if self.status == 'IDLE' and self.round is not None:
                self.round.status = 'IDLE'
            self.job.reschedule(trigger="interval", seconds=10)

        round_ = await get_round_info()
        if self.round is None or round_ != self.round:
            self.round = round_
            if self.round.status == 'STARTED':
                for downloader in self.downloaders.values():
                    if downloader is not None:
                        await downloader.start(self.round)
                        await asyncio.sleep(0.5)
                self.status = "STARTED"
            else:
                for downloader in self.downloaders.values():
                    if downloader is not None:
                        await downloader.end()
                self.status = "IDLE"
        else:
            if self.round.status == 'STARTED':
                for downloader in self.downloaders.values():
                    if downloader is not None and downloader.cid == -1:
                        await downloader.start(self.round)

    async def close(self):
        for downloader in self.downloaders.values():
            if downloader is not None:
                await downloader.close()
        self.scheduler.shutdown()
        self.logger.info("Manager closed")

    def get_req(self, role: str) -> Union[LiveStreamReq, None]:
        for req in self.reqs:
            if req.role == role:
                return req
        return None

    def get(self) -> ManagerInfo:
        downloaders = []
        for role, downloader in self.downloaders.items():
            if downloader is None:
                downloaders.append(DownloaderInfo(name=role, status=False, error_count=0))
            else:
                downloaders.append(DownloaderInfo(
                    name=role,
                    status=(self.round.status == 'STARTED'),
                    error_count=downloader.error_count,
                    quality=self.get_req(role).quality,
                    recorded=round(sum([it.duration for it in downloader.segments]))
                ))
        return ManagerInfo(round_info=self.round, downloaders=downloaders)

    def _save_reqs(self):
        reqs = [it.dict() for it in self.reqs]
        with open(config.reqs_json, "w") as f:
            json.dump(reqs, f)

    async def delete_req(self, role: str):
        downloader = self.downloaders.get(role, None)
        if downloader is not None:
            await downloader.close()
            del self.downloaders[role]
        self.reqs = [req for req in self.reqs if req.role != role]
        self._save_reqs()
        await self.scan()


    async def add_req(self, req: LiveStreamReq):
        if req.role in self.downloaders:
            return
        self.reqs.append(req)
        self._save_reqs()
        await self.scan()

    async def update_req(self, role: str, quality: str):
        req = LiveStreamReq(role=role, quality=quality)
        await self.delete_req(role)
        await self.add_req(req)


if __name__ == '__main__':
    async def main():
        manager = Manager([
            LiveStreamReq(quality="1080p", role="主视角"),
            LiveStreamReq(quality="540p", role="红方英雄"),
            LiveStreamReq(quality="540p", role="蓝方英雄"),
            LiveStreamReq(quality="540p", role="红方工程"),
            LiveStreamReq(quality="540p", role="蓝方工程"),
            LiveStreamReq(quality="540p", role="红方3号步兵"),
            LiveStreamReq(quality="540p", role="蓝方3号步兵"),
            LiveStreamReq(quality="540p", role="红方4号步兵"),
            LiveStreamReq(quality="540p", role="蓝方4号步兵"),
        ])
        await manager.init()
        await asyncio.sleep(3600 * 2)
        await manager.close()

    asyncio.run(main())
