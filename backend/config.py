from pathlib import Path

port = 10398

save_dir = Path('data')
max_error_count = 20
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "rtmp.djicdn.com",
    "Origin": "https://www.robomaster.com",
    "Pragma": "no-cache",
    "Referer": "https://www.robomaster.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}
oss_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Cache-Control': 'no-cache,no-store',
    'Connection': 'keep-alive',
    'Host': 'pro-robomasters-hz-n5i3.oss-cn-hangzhou.aliyuncs.com',
    'Origin': 'https://www.robomaster.com',
    'Pragma': 'no-cache',
    'Referer': 'https://www.robomaster.com/',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}

round_info_url = "https://pro-robomasters-hz-n5i3.oss-cn-hangzhou.aliyuncs.com/live_json/current_and_next_matches.json"
live_info_url = "https://pro-robomasters-hz-n5i3.oss-cn-hangzhou.aliyuncs.com/live_json/live_game_info.json"

reqs_json = Path("reqs.json")

basic_security = True
username = b"nuaanuaa"
password = b"ckyfckyf"
