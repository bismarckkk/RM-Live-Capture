import { useRef } from "react";
import type { ProColumns, ActionType } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { Space, message } from 'antd';
import ConvertButton from "@/components/convertButton";
import DownloadButton from "@/components/downloadButton";
import OptionsAction from "@/components/optionsAction";
import { Link } from "umi";

import axios from "axios";

export const waitTimePromise = async (time: number = 100) => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(true);
        }, time);
    });
};

export const waitTime = async (time: number = 100) => {
    await waitTimePromise(time);
};

interface ApiResult {
    code: number;
    msg: string;
}

interface VideoItem {
    title: string;
    red: string;
    blue: string;
    role: string;
    round: number;
    file_name: string;
}

const roles = [
    '主视角', '红方英雄', '蓝方英雄', '红方工程', '蓝方工程', '红方3号步兵',
    '蓝方3号步兵', '红方4号步兵', '蓝方4号步兵', '红方空中', '蓝方空中'
]

const columns: ProColumns<VideoItem>[] = [
    {
        title: 'Title',
        dataIndex: 'title',
        ellipsis: true,
        search: false,
        width: 450
    },
    {
        title: 'Red',
        dataIndex: 'red',
    },
    {
        title: 'Blue',
        dataIndex: 'blue',
    },
    {
        title: 'Role',
        dataIndex: 'role',
        valueType: 'select',
        valueEnum: roles.reduce((acc: any, cur) => {
            acc[cur] = { text: cur };
            return acc;
        }, {})
    },
    {
        title: 'Round',
        dataIndex: 'round',
        search: false,
        valueType: 'select',
        valueEnum: [1, 2, 3, 4, 5].reduce((acc: any, cur) => {
            acc[cur] = { text: `Round ${cur}` };
            return acc;
        }, {})
    },
    {
        title: 'Action',
        valueType: 'option',
        key: 'option',
        width: 300,
        render: (_, record, __, action) => <Space size="middle">
            <ConvertButton filename={record.file_name}/>
            <a
                onClick={async () => {
                    try {
                        const data = await axios.get<ApiResult>(`/api/video/delete/${record.file_name}`);
                        if (data.data.code !== 0) {
                            message.error(data.data.msg);
                        } else {
                            action?.reload();
                        }
                    } catch (_) {

                    }
                }}
            >
                Delete
            </a>
            <DownloadButton filename={record.file_name} title={record.title}/>
            <Link
                target="_blank"
                to={`/play?fn=${record.file_name}`}
            >
                Play
            </Link>
        </Space>,
    },
];

export default () => {
    const actionRef = useRef<ActionType>();
    return (
        <ProTable<VideoItem>
            actionRef={actionRef}
            columns={columns}
            request={async (params) => {
                let data = (await axios.post('/api/video/list', params)).data;
                data.success = true;
                return data;
            }}
            rowKey="title"
            search={{
                labelWidth: 'auto',
                collapsed: false,
            }}
            options={{
                setting: {
                    listsHeight: 400,
                },
            }}
            ghost={true}
            pagination={{
                defaultPageSize: 15,
                pageSizeOptions: [10, 15, 20, 100]
            }}
            rowSelection={{}}
            tableAlertRender={({
                selectedRowKeys,
                selectedRows,
                onCleanSelected,
            }) => {
                return (
                    <span>
                      已选 {selectedRowKeys.length} 项
                      <a style={{marginInlineStart: 8}} onClick={onCleanSelected}>
                        取消选择
                      </a>
                    </span>
                );
            }}
            tableAlertOptionRender={({
                 selectedRows,
                 onCleanSelected,
            }) => {
                return (
                    <OptionsAction rows={selectedRows} reload={() => {
                        onCleanSelected();
                        actionRef.current?.reload();
                    }} />
                );
            }}
        />
    );
};
