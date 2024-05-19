import React, { useState, useRef } from 'react';
import {Button, message} from "antd";

import axios from "axios";

interface ApiResult {
    code: number;
    msg: string;
}

function DownloadButton({filename = "", title = ""}) {
    const [loading, setLoading] = useState(false);
    const aRef = useRef<HTMLAnchorElement>(null);
    return (
        <div>
            <a
                target="_blank"
                href={`/api/video/download/${filename}`}
                download={`${title}.mp4`}
                ref={aRef}
            />
            <Button
                type="link"
                loading={loading}
                onClick={async () => {
                    try {
                        setLoading(true);
                        const data = await axios.get<ApiResult>(`/api/video/convert/${filename}`);
                        setLoading(false);
                        if (data.data.code !== 0) {
                            message.error(data.data.msg);
                        } else {
                            aRef.current?.click();
                        }
                    } catch (_) {

                    }
                }}
                style={{padding: 0}}
            >
                Download
            </Button>
        </div>
    );
}

export default DownloadButton;