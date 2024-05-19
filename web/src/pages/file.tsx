import type { ProColumns } from '@ant-design/pro-components';
import { ProTable } from '@ant-design/pro-components';
import { Space } from 'antd';
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
        width: 250,
        render: (_, record) => <Space size="middle">
            <a
                onClick={() => {
                    console.log('convert to mp4', record.file_name)
                }}
            >
                To MP4
            </a>
            <a
                onClick={() => {
                    console.log('Delete', record.file_name)
                }}
            >
                Delete
            </a>
            <a
                onClick={() => {
                    console.log('Download', record.file_name)
                }}
            >
                Download
            </a>
            <a
                onClick={() => {
                    console.log('Play', record.file_name)
                }}
            >
                Play
            </a>
        </Space>,
    },
];

export default () => {
    return (
        <ProTable<VideoItem>
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
        />
    );
};
