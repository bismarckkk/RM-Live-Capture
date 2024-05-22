import React, { Component, createRef } from 'react';
import { ProList } from "@ant-design/pro-components";
import { Button, Tag, Result, Flex, Space, Modal } from "antd";
import { PlusOutlined, ReloadOutlined, ExclamationCircleFilled } from "@ant-design/icons";
import Loading from "@/loading";
import StreamModal from "@/components/streamModal";

import axios from "axios";
import {sec2str} from "@/utils";

const { confirm } = Modal;

interface Downloader {
    name: string;
    status: boolean;
    error_count: number;
    quality: string;
    recorded: number;
}

interface RoundInfo {
    red: string;
    blue: string;
    round: number;
    id: number;
    status: string;
}

interface ManagerInfo {
    round_info: RoundInfo;
    downloaders: Downloader[];
}

export interface LiveInfo {
    live: boolean;
    streams: {[propName: string]: {"1080p"?: string, "720p"?: string, "540p"?: string}};
}

export interface LiveStreamRequest {
    quality: string;
    role: string;
}

class Index extends Component {
    state : {
        downloaders: Downloader[],
        round: RoundInfo,
        live: LiveInfo,
        loading: boolean,
        error: null | string,
    } = {
        downloaders: [],
        round: {
            red: "Null",
            blue: "Null",
            round: 0,
            id: 0,
            status: "IDLE"
        },
        live: {
            live: false,
            streams: {}
        },
        loading: true,
        error: null,
    }

    streamModal = createRef<StreamModal>();
    timer: NodeJS.Timeout | null = null;

    async refresh() {
        try {
            const managerInfo = await axios.get<ManagerInfo>("/api/manager");
            const liveInfo = await axios.get<LiveInfo>("/api/manager/live");
            this.setState({
                downloaders: managerInfo.data.downloaders,
                round: managerInfo.data.round_info,
                live: liveInfo.data,
                loading: false
            });
        } catch (e: any) {
            console.error(e);
            this.setState({error: e.message, loading: false})
        }
    }

    async componentDidMount() {
        await this.refresh();
        if (!this.timer) {
            this.timer = setInterval(this.refresh.bind(this), 10000);
        }
    }

    async componentWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }

    async addDownloader() {
        const req = await this.streamModal.current?.open(this.state.live);
        if (req) {
            await axios.get(`/api/manager/add?role=${req.role}&quality=${req.quality}`);
            await this.refresh();
        }
    }

    async editDownloader(role: string) {
        const req = await this.streamModal.current?.open(this.state.live, role);
        if (req) {
            await axios.get(`/api/manager/update?role=${req.role}&quality=${req.quality}`);
            await this.refresh();
        }
    }

    async deleteDownloader(role: string) {
        const that = this;
        confirm({
            title: 'Warning',
            content: 'Do you want to delete this Downloader?',
            icon: <ExclamationCircleFilled />,
            async onOk() {
                await axios.get(`/api/manager/delete?role=${role}`);
                await that.refresh();
            },
        });
    }

    render() {
        const listData = this.state.downloaders.map((downloader) => ({
            title: downloader.name,
            subTitle: downloader.status ?
                <Tag bordered={false} color="blue">Running</Tag> :
                <Tag bordered={false} color="red">Idle</Tag>,
            actions: [
                <Button type="link" size="small" onClick={this.editDownloader.bind(this, downloader.name)}>
                    Edit
                </Button>,
                <Button type="link" size="small" onClick={this.deleteDownloader.bind(this, downloader.name)}>
                    Delete
                </Button>
            ],
            content: (
                <div>
                    <p>Recorded: {sec2str(downloader.recorded)}</p>
                    <p>Error Count: {downloader.error_count}</p>
                    <p>Quality: {downloader.quality}</p>
                </div>
            )
        }))

        let list = <Loading />
        if (!this.state.loading) {
            if (this.state.error === null) {
                list = <ProList<any>
                    ghost={true}
                    itemCardProps={{
                        ghost: true,
                    }}
                    showActions="hover"
                    grid={{ gutter: 16, column: 3 }}
                    metas={{
                        title: {},
                        subTitle: {},
                        type: {},
                        avatar: {},
                        content: {},
                        actions: {cardActionProps: "extra"},
                    }}
                    dataSource={listData}
                />
            } else {
                list = <Result
                    status="error"
                    title="Error"
                    subTitle={this.state.error}
                />
            }
        }

        return (
            <div>
                <StreamModal ref={this.streamModal}/>
                <Flex justify="space-between" align="center" style={{width: "100%"}}>
                    <div>
                        {
                            this.state.live.live ?
                                <div>
                                    {
                                        this.state.round.status === "IDLE" ?
                                            <h2>Waiting Match</h2> :
                                            <Space size="middle">
                                                <h2>Living</h2>
                                                <h3>{
                                                    `${this.state.round.red} vs ${this.state.round.blue} Round ${this.state.round.round}`
                                                }</h3>
                                            </Space>
                                    }
                                </div> : <h2>Idle</h2>
                        }
                    </div>
                    <div>
                        <Space.Compact block>
                            <Button icon={<PlusOutlined/>} onClick={this.addDownloader.bind(this)}/>
                            <Button icon={<ReloadOutlined/>} onClick={async () => {
                                this.setState({loading: true});
                                await this.refresh()
                            }}/>
                        </Space.Compact>
                    </div>
                </Flex>
                { list }
            </div>
        );
    }
}

export default Index;
