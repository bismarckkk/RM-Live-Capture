import { useEffect, useRef } from "react";
import { Modal } from "antd";

import axios from "axios";
import Hls from "hls.js";

export default function Video({ src = "", className = '', ...props }) {
    const videoRef = useRef<HTMLVideoElement>(null);

    if (src !== '/api/video/file/') {
        useEffect(()=>{
            const hls = new Hls();
            if (Hls.isSupported()) {
                hls.loadSource(src);
                hls.attachMedia(videoRef.current!);
                hls.on(Hls.Events.ERROR, (err, data) => {
                    if (data.fatal) {
                        try {
                            if (data.networkDetails.response) {
                                const error = JSON.parse(data.networkDetails.response);
                                Modal.error({
                                    title: 'Error',
                                    content: error.msg,
                                });
                            }
                        } catch (_) {
                            Modal.error({
                                title: 'Error',
                                content: data.error.message,
                            });
                        }

                        hls.destroy();
                    }
                });
            }
        },[src])
    }

    return (
        <video
            ref={videoRef}
            controls
            {...props}
            src={src}
            className={className}
        />
    )
}
