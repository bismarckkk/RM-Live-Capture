import React, {Component} from 'react';
import { ModalForm, ProFormSelect } from "@ant-design/pro-form";
import { message } from "antd";

import { LiveInfo, LiveStreamRequest } from "@/pages";

class StreamModal extends Component {
    state : {
        open: boolean,
        live: LiveInfo,
        role: string
    } = {
        open: false,
        live: { live: false, streams: {} },
        role: ""
    };

    resolve: (req: LiveStreamRequest) => void = () => {};
    reject: (reason?: any) => void = () => {};

    open(live: LiveInfo, role: string = "") {
        return new Promise<LiveStreamRequest>((resolve, reject) => {
            this.resolve = resolve;
            this.reject = reject;
            this.setState({ open: true, live, role: role });
        })
    }

    render() {
        return (
            <ModalForm<LiveStreamRequest>
                title="Start Stream"
                open={this.state.open}
                onOpenChange={(open) => {
                    this.setState({open})
                    this.reject()
                }}
                onFinish={async (values) => {
                    if (!(values.quality in this.state.live.streams[values.role])) {
                        message.error("Quality not available");
                        return false;
                    }
                    this.resolve(values);
                    return true;
                }}
            >
                <ProFormSelect
                    name="role"
                    label="Role"
                    initialValue={this.state.role !== "" ? this.state.role : null}
                    disabled={this.state.role !== ""}
                    options={
                        Object.keys(this.state.live.streams).map((role) => ({
                            label: role, value: role
                        }))
                    }
                    placeholder="Please select a role"
                    rules={[{ required: true, message: 'Please select a role' }]}
                />
                <ProFormSelect
                    name="quality"
                    label="Quality"
                    options={[
                        { label: "1080p", value: "1080p" },
                        { label: "720p", value: "720p" },
                        { label: "540p", value: "540p" },
                    ]}
                    placeholder="Please select a quality"
                    rules={[{ required: true, message: 'Please select a quality' }]}
                />
            </ModalForm>
        );
    }
}

export default StreamModal;