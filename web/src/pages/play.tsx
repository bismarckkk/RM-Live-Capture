import React, { useState } from 'react';
import { Input, Button, Space } from "antd";
import Video from "@/components/video";

import { useLocation } from "umi";
import { getQuery } from "@/utils";

function Play() {
    const [fn, setFn] = useState("");
    const [input, setInput] = useState(fn);
    const location = useLocation();
    const query = getQuery(location.search);
    if (query.fn) {
        if (fn !== query.fn) {
            setFn(query.fn);
            setInput(query.fn);
            location.search = "";
        }
    }
    return (
        <Space direction="vertical" size="middle" style={{width: "100%", height: "100%"}}>
            <Space.Compact style={{width: "100%"}}>
                <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Enter Video Name"
                />
                <Button
                    type="primary"
                    onClick={() => {
                        setFn(input);
                    }}
                >
                    Go
                </Button>
            </Space.Compact>
            <Video src={`/api/video/file/${fn}`} style={{width: "100%", height: "100%"}}/>
        </Space>
    );
}

export default Play;