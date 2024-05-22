import time
from typing import List, Union
import random
import asyncio
import re

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from pydantic import BaseModel

import config
from logger import getLogger


name_regex = re.compile(r"/(\d+_\d+)\.ts")


class Segment(BaseModel):
    duration: float
    uri: str


class RoundInfo(BaseModel):
    red: str
    blue: str
    round: int
    id: int
    status: str

    def __eq__(self, other):
        return (self.red == other.red and self.blue == other.blue and self.round == other.round and
                self.id == other.id and self.status == other.status)


class Downloader:
    def __init__(self, name: str, url: str, scheduler: AsyncIOScheduler):
        self.name = name
        self.id = random.randint(0, 100000)
        self.cid = -1
        self.rid = 1
        self.title = "Null Vs Null R0"
        self.processing = False
        self.url = url
        self.error_count = 0
        self.scheduler = scheduler
        self.connector = aiohttp.TCPConnector(limit=4)
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            headers=config.headers
        )

        self.segments: List[Segment] = []
        self.job: Union[Job, None] = None
        self.logger = getLogger(f"DL-{self.name}", "INFO")
        
    async def start(self, info: RoundInfo):
        if self.job is not None:
            await self.end()
        self.cid = info.id
        self.rid = info.round
        self.segments = []
        self.title = f"{info.red} Vs {info.blue} {self.name} R{info.round}"
        self.job = self.scheduler.add_job(self._get_m3u8_info, "interval", seconds=3)
        self.logger.info(f"Start {self.name} {self.title}")
        self.logger.info(f"URL: {self.url}")

    async def split(self):
        await self.end()
        self.job = self.scheduler.add_job(self._get_m3u8_info, "interval", seconds=3)
        self.logger.info(f"Split {self.name} {self.title}")

    async def end(self):
        if self.job is not None:
            self.job.remove()
            self.job = None
        while self.processing:
            await asyncio.sleep(1)
        await self._save()
        self.segments = []
        self.logger.info(f"End {self.name} {self.title}")

    async def close(self):
        await self.end()
        await self.connector.close()
        await self.session.close()
        self.logger.info(f"Close {self.name}")

    async def _save(self):
        if not self.segments:
            return
        with open(config.save_dir / f"{self.id}_{self.cid}_{self.rid}_{int(time.time())}.m3u8", "w") as f:
            f.write("#EXTM3U\n")
            f.write("#EXT-X-TARGETDURATION:4\n")
            f.write("#EXT-X-PLAYLIST-TYPE:VOD\n")
            f.write(f"#TITLE:{self.title} {int(time.time())}\n")
            for segment in self.segments:
                f.write(f"#EXTINF:{segment.duration},\n")
                f.write(f"{self._get_segment_name(segment)}\n")
            f.write("#EXT-X-ENDLIST\n")
        self.logger.info(f"Save {self.name} {self.title}")

    async def _get_m3u8_info(self):
        if self.processing:
            self.error_count += 1
            self.logger.error(f"M3U8 processing timeout")
            return
        self.logger.debug(f"Getting m3u8 info")
        try:
            self.processing = True
            async with self.session.get(self.url) as response:
                text = await response.text()
                lines = text.split("\n")
                duration = 3
                segments = []
                for i in range(len(lines)):
                    line = lines[i].replace(' ', '')
                    if line.startswith("#EXTINF"):
                        duration = float(line.split(":")[1].split(",")[0])
                        segments.append(Segment(duration=duration, uri=lines[i + 1]))
                self.job.reschedule("interval", seconds=duration)
                await self._download_segments(segments)
            if len(segments) > 750:
                await self.split()
            self.processing = False
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"Error {e.status} on {self.name}")
            if e.status == 404:
                await self.end()
            else:
                self.error_count += 1
                if self.error_count > config.max_error_count:
                    self.logger.fatal(f"Error count exceed {config.max_error_count} on {self.name}")
                    self.error_count = 0
                    await self.split()
        except Exception as e:
            self.logger.error(f"Error {e} on {self.name}")
            
    def _get_segment_name(self, segment: Segment):
        id_ = name_regex.findall(segment.uri)[0].replace("_", "-")
        return f"{self.id}_{self.cid}_{self.rid}_{id_}.ts"
                    
    async def _download_segment(self, segment: Segment):
        already = [s.uri for s in self.segments[-5:]]
        if segment.uri in already:
            return
        self.logger.debug(f"Downloading {segment.uri}")
        async with self.session.get(f"https://rtmp.djicdn.com/robomaster/{segment.uri}") as response:
            filename = config.save_dir / self._get_segment_name(segment)
            with open(filename, "wb") as f:
                f.write(await response.read())
            self.segments.append(segment)
        
    async def _download_segments(self, segments: List[Segment]):
        for segment in segments:
            try:
                await self._download_segment(segment)
            except Exception as _:
                try:
                    await self._download_segment(segment)
                except aiohttp.ClientResponseError as e:
                    self.logger.error(e.status, e.message)
                    self.error_count += 1
                except Exception as e:
                    self.logger.error(e)


if __name__ == "__main__":
    async def main():
        scheduler = AsyncIOScheduler()
        scheduler.start()
        downloader = Downloader("主视角", "https://rtmp.djicdn.com/robomaster/ual2024-beibu.m3u8?auth_key=1714034239-0-0-58bb9500239eec501606d2dab3004f66", scheduler)
        await downloader.start(RoundInfo(red="同济大学", blue="齐鲁工业大学", round=3, id=19012))
        await asyncio.sleep(60)
        await downloader.close()
        scheduler.shutdown()

    asyncio.run(main())

