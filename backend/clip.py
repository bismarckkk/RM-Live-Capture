from pathlib import Path
from datetime import timedelta
import time

import m3u8

data_folder = Path("z:/rmuc record/data2/nuaa")


def str_to_timedelta(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def get_new_name(path: Path):
    name = path.stem
    name = name[:name.rfind('_')]
    name += '_' + str(int(time.time()))
    # name += '_1722580709'
    return path.with_name(name + path.suffix)


def load_m3u8_file(m3u8_path):
    with open(m3u8_path, 'r', encoding='utf-8') as f:
        m3u8_content = f.read()
    m3u8_obj = m3u8.M3U8(m3u8_content)
    return m3u8_obj


def m3u8_obj_to_str(m3u8_obj, old_path: Path):
    title = "Null Vs Null"
    with old_path.open('r', encoding='utf-8') as f:
        for line in f.readlines():
            if line.startswith("#TITLE:"):
                title = line.replace("#TITLE:", "").strip()
                break

    items = title.split(" ")
    role = items[3]

    lines = ['#EXTM3U', '#EXT-X-TARGETDURATION:4', '#EXT-X-PLAYLIST-TYPE:VOD',
             f'#TITLE:南京航空航天大学 Vs 中国石油大学 {role} R2 {str(int(time.time()))}']

    for segment in m3u8_obj.segments:
        lines.append('#EXTINF:{},'.format(segment.duration))
        lines.append(segment.uri)

    lines.append('#EXT-X-ENDLIST')

    return '\n'.join(lines)


def cut_m3u8_file(m3u8_path, start_time, end_time):
    # Load the m3u8 file
    m3u8_obj = load_m3u8_file(str(m3u8_path))

    # Create a new m3u8 object for the cut segments
    new_m3u8_obj = m3u8.M3U8()

    # Initialize a variable to keep track of the cumulative duration
    cumulative_duration = timedelta()

    # Iterate over the segments in the m3u8 file
    for segment in m3u8_obj.segments:
        # Add the duration of the current segment to the cumulative duration
        cumulative_duration += timedelta(seconds=segment.duration)

        # Check if the cumulative duration is within the start and end time
        if start_time <= cumulative_duration <= end_time:
            # If it is, add the segment to the new m3u8 object
            new_m3u8_obj.segments.append(segment)

    # Save the new m3u8 object to a file
    with get_new_name(m3u8_path).open('w', encoding='utf-8') as f:
        f.write(m3u8_obj_to_str(new_m3u8_obj, m3u8_path))


start_time = str_to_timedelta("1:42:00")
end_time = str_to_timedelta("1:55:00")


for it in data_folder.glob("*.m3u8"):
    cut_m3u8_file(it, start_time, end_time)
