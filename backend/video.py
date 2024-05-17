from typing import List

from pydantic import BaseModel

import config


class Video(BaseModel):
    title: str
    red: str
    blue: str
    role: str
    round: int
    file_name: str


def get_video_list() -> List[Video]:
    res = []
    for it in config.save_dir.glob("*.m3u8"):
        title = "Null Vs Null"
        with it.open('r') as f:
            for line in f.readlines():
                if line.startswith("#TITLE:"):
                    title = line.replace("#TITLE:", "").strip()
                    break
        items = title.split(" ")
        if len(items) != 6:
            continue
        res.append(Video(
            title=title,
            red=items[0],
            blue=items[2],
            role=items[3],
            round=int(items[4][1:]),
            file_name=it.name
        ))
    return res


def convert_to_mp4(video: Video):
    import ffmpeg
    ffmpeg.input(str(config.save_dir / video.file_name)).output(
        str(config.save_dir / f"{video.title} {video.file_name.split('_')[-1]}.mp4"),
        acodec="copy", vcodec="copy"
    ).run(overwrite_output=True)


if __name__ == '__main__':
    for video in get_video_list():
        convert_to_mp4(video)
