export interface ApiResult {
    code: number;
    msg: string;
}

export interface VideoItem {
    title: string;
    red: string;
    blue: string;
    role: string;
    round: number;
    duration: number;
    file_name: string;
}

export const getQuery = (search: string) => {
    const str = search.slice(1)
    const arr = str.split('&')
    const result: any = {}
    for (let i = 0; i < arr.length; i++) {
        const item = arr[i].split('=')
        result[item[0]] = item[1]
    }
    return result
}

export function sec2str(sec: number) {
    sec = Math.round(sec)
    const minutes = Math.floor(sec / 60);
    let seconds = (sec % 60).toString();
    if (seconds.length === 1) {
        seconds = '0' + seconds;
    }
    return `${minutes}:${seconds}`;
}
