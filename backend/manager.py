from typing import List, Dict, Union
import json
import asyncio
import traceback
from datetime import datetime

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from pydantic import BaseModel
from asyncache import cached
from cachetools import TTLCache

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
    manual_mode: bool
    downloaders: List[DownloaderInfo]


async def get_round_info() -> RoundInfo:
    async with aiohttp.ClientSession(headers=config.oss_headers, timeout=aiohttp.ClientTimeout(total=10)) as session:
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


def convert_live_info(live_info: dict, info: dict):
    mainStream = live_string_to_dict(live_info['zoneLiveString'])
    if mainStream:
        info['streams']['主视角'] = mainStream
    for fpv in live_info['fpvData']:
        stream = live_string_to_dict(fpv['sources'])
        if stream:
            info['streams'][fpv['role']] = stream


def check_date_position(dates: List[str]) -> int:
    date_objects = [datetime.strptime(date, "%Y-%m-%d").date() for date in dates]
    today = datetime.today().date()

    if today > min(date_objects):
        return -1
    elif today < max(date_objects):
        nearest_date = max(date_objects)
        days_diff = (nearest_date - today).days
        return days_diff
    else:
        return 0


@cached(TTLCache(1, 5))
async def get_live_info() -> LiveInfo:
    default_event_index = 0
    async with aiohttp.ClientSession(headers=config.oss_headers, timeout=aiohttp.ClientTimeout(total=10)) as session:
        async with session.get(config.live_info_url) as response:
            data = json.loads(await response.text())['eventData']
            info = {
                "live": False,
                "streams": {}
            }
            zoneName = 'Not Got'
            ok = False
            for live_info in data:
                if live_info['liveState'] != 1 or live_info['matchState'] != 1:
                    continue
                ok = True
                info['live'] = True
                zoneName = live_info['zoneName']
                convert_live_info(live_info, info)
            if not ok:
                live_info = data[default_event_index]
                min_date_diff = 99999
                for _live_info in data:
                    date_diff = check_date_position(_live_info['zoneDate'])
                    if date_diff == 0:
                        break
                    if date_diff == -1:
                        continue
                    if date_diff < min_date_diff:
                        min_date_diff = date_diff
                        live_info = _live_info

                convert_live_info(live_info, info)
                zoneName = live_info['zoneName']
            print(f"Got {zoneName} Live Info")
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
        self.manual_mode = False

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
        try:
            await self._scan()
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Error: {e}")

    async def manual_start(self):
        _round = RoundInfo(red="红方", blue="蓝方", round=1, id=99999, status="STARTED")
        self.manual_mode = True
        for downloader in self.downloaders.values():
            if downloader is not None and downloader.cid == -1:
                await downloader.start(_round)

    async def manual_end(self):
        for downloader in self.downloaders.values():
            if downloader is not None:
                await downloader.end()
        self.manual_mode = False

    async def _scan(self):
        self.logger.info("Scanning...")
        live_info = await get_live_info()
        for req in self.reqs:
            stream = live_info.streams.get(req.role, {}).get(req.quality)
            if stream is not None:
                if self.downloaders.get(req.role) is None:
                    self.downloaders[req.role] = Downloader(req.role, stream, self.scheduler)
                else:
                    self.downloaders[req.role].url = stream

        if not self.manual_mode:
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
                    status=(self.manual_mode or (self.round is not None and
                                                 self.round.status == 'STARTED' and
                                                 len(downloader.segments) > 0)),
                    error_count=downloader.error_count,
                    quality=self.get_req(role).quality,
                    recorded=round(sum([it.duration for it in downloader.segments]))
                ))
        _round = self.round
        if _round is None:
            _round = RoundInfo(red="Null", blue="Null", round=0, id=0, status="IDLE")
        return ManagerInfo(round_info=_round, manual_mode=self.manual_mode, downloaders=downloaders)

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
