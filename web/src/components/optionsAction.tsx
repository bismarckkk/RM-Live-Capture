import {useState} from 'react';
import { Space, Progress, Button, message } from "antd";

import axios from "axios";
import { VideoItem, ApiResult } from "@/utils";

function OptionsAction({rows, reload}: {rows: VideoItem[], reload: () => void}) {
    const [current, setCurrent] = useState(-1);
    const total = rows.length;

    async function doAction(action: (filename: string) => Promise<any>) {
        for (let i = 0; i < rows.length; i++) {
            setCurrent(i);
            await action(rows[i].file_name);
        }
        message.success('Operation Success');
        setCurrent(-1);
        reload();
    }

    return (
        <Space size="middle">
            {current > 0 && <Progress percent={Math.round(current / total * 100)} style={{width: 200}} status="active" />}
            <Button type="link" style={{padding: 0}} disabled={current > 0}
                onClick={async () => {
                    await doAction(async (filename) => {
                        const data = await axios.get<ApiResult>(`/api/video/convert/${filename}`);
                        if (data.data.code !== 0) {
                            message.error(data.data.msg);
                        }
                    });
                }}
            >
                Convert Selected
            </Button>
            <Button type="link" style={{padding: 0}} disabled={current > 0}
                onClick={async () => {
                    await doAction(async (filename) => {
                        const data = await axios.get<ApiResult>(`/api/video/delete/${filename}`);
                        if (data.data.code !== 0) {
                            message.error(data.data.msg);
                        }
                    });
                }}
            >
                Delete Selected
            </Button>
        </Space>
    );
}

export default OptionsAction;