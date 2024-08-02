import { useState, useRef } from 'react';
import { Space, Progress, Button, message } from "antd";

import axios from "axios";
import { VideoItem, ApiResult } from "@/utils";
import LoginModal from "@/components/loginModal";
import FormModal from "@/components/formModal";


function copyToClipboard(textToCopy: string) {
    // navigator clipboard 需要https等安全上下文
    if (navigator.clipboard && window.isSecureContext) {
        // navigator clipboard 向剪贴板写文本
        return navigator.clipboard.writeText(textToCopy);
    } else {
        // 创建text area
        let textArea = document.createElement("textarea");
        textArea.value = textToCopy;
        textArea.style.position = "absolute";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        return new Promise<string>((res: Function, rej: Function) => {
            // 执行复制命令并移除文本框
            document.execCommand('copy') ? res() : rej();
            textArea.remove();
        });
    }
}


function OptionsAction({rows, reload}: {rows: VideoItem[], reload: () => void}) {
    const [current, setCurrent] = useState(-1);
    const loginModalRef = useRef<LoginModal>(null);
    const formModalRef = useRef<FormModal>(null);
    const total = rows.length;

    async function doAction(action: (filename: string) => Promise<any>, text='Operation Success') {
        for (let i = 0; i < rows.length; i++) {
            setCurrent(i);
            await action(rows[i].file_name);
        }
        if (text !== "") {
            message.success(text);
        }
        setCurrent(-1);
        reload();
    }

    return (
        <Space size="middle">
            {current > 0 && <Progress percent={Math.round(current / total * 100)} style={{width: 200}} status="active" />}
            <Button type="link" style={{padding: 0}} disabled={current > 0}
                    onClick={async () => {
                        const data = await axios.get<ApiResult>(`/api/bili/username`);
                        if (data.data.msg === '请先登录') {
                            message.info('Please login first');
                            loginModalRef.current?.open();
                        } else {
                            const videos = rows.map(row => row.file_name);
                            const title = await formModalRef.current?.open(`You are uploading as ${data.data.msg}`);
                            message.info('Preprocessing, please wait...')
                            await doAction(async (filename) => {
                                const data = await axios.get<ApiResult>(`/api/video/convert/${filename}`);
                                if (data.data.code !== 0) {
                                    message.error(data.data.msg);
                                }
                            }, "");
                            await axios.post<ApiResult>(`/api/bili/upload?title=${title}`, videos)
                            message.success('Uploading on background. You can close the page now.')
                        }
                    }}
            >
                Upload to Bilibili
            </Button>
            <Button type="link" style={{padding: 0}} disabled={current > 0}
                    onClick={async () => {
                        let res = ""
                        for (let i = 0; i < rows.length; i++) {
                            res += rows[i].role + ' ' + window.location.origin + '/api/video/file/' + rows[i].file_name + '\n';
                        }
                        try {
                            await copyToClipboard(res);
                            message.success('Text copied to clipboard');
                        } catch (err) {
                            message.error('Failed to copy text! ' + err);
                        }
                    }}
            >
                Export Play List
            </Button>
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
            <LoginModal ref={loginModalRef} />
            <FormModal ref={formModalRef} />
        </Space>
    );
}

export default OptionsAction;