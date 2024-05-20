import React, { useState } from 'react';
import {Button, message} from "antd";

import axios from "axios";
import { ApiResult } from "@/utils";

function ConvertButton({filename = ""}) {
    const [loading, setLoading] = useState(false);
    return (
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
                        message.success('Convert Success');
                    }
                } catch (_) {

                }
            }}
            style={{padding: 0}}
        >
            To MP4
        </Button>
    );
}

export default ConvertButton;