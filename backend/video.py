from typing import List, Union
import asyncio

from pydantic import BaseModel

import config


class Video(BaseModel):
    title: str
    red: str
    blue: str
    role: str
    round: int
    file_name: str


def get_video_info(file_name: str) -> Union[Video, None]:
    title = "Null Vs Null"
    with (config.save_dir / file_name).open('r', encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith("#TITLE:"):
                title = line.replace("#TITLE:", "").strip()
                break
    items = title.split(" ")
    if len(items) != 6:
        return None
    return Video(
        title=title,
        red=items[0],
        blue=items[2],
        role=items[3],
        round=int(items[4][1:]),
        file_name=file_name
    )


def get_video_list() -> List[Video]:
    res = []
    for it in config.save_dir.glob("*.m3u8"):
        _video = get_video_info(it.name)
        if _video is not None:
            res.append(_video)
    return res


async def convert_to_mp4(_video: Video):
    def run():
        import ffmpeg
        ffmpeg.input(str(config.save_dir / _video.file_name)).output(
            str(config.mp4_dir / f"{_video.title}.mp4"),
            acodec="copy", vcodec="copy"
        ).run(overwrite_output=True)

    await asyncio.to_thread(run)


def delete_file(_video: Video):
    with open(config.save_dir / _video.file_name, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                file = config.save_dir / lines[i + 1]
                if file.exists():
                    file.unlink()
    (config.save_dir / _video.file_name).unlink()


if __name__ == '__main__':
    for _video in get_video_list():
        convert_to_mp4(_video)
