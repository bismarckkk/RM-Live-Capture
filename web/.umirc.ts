import {defineConfig} from "umi";

export default defineConfig({
    npmClient: 'yarn',
    publicPath: '/static/',
    history: {type: 'hash'},
    plugins: [
        '@umijs/plugins/dist/antd',
    ],
    antd: {},
    title: 'RM Recorder',
    proxy: {
        '/api': {
            'target': 'http://192.168.1.4:10398/',
            'changeOrigin': true,
        },
    },
});
