import {defineConfig} from "umi";

export default defineConfig({
    npmClient: 'yarn',
    publicPath: '/static/',
    history: {type: 'hash'},
    plugins: [
        '@umijs/plugins/dist/antd',
    ],
    antd: {},
    title: 'RM Live Capture',
    proxy: {
        '/api': {
            'target': 'http://127.0.0.1:10398/',
            'changeOrigin': true,
            onProxyReq: (proxyReq, req, res) => {
                const username = 'nuaanuaa';
                const password = 'ckyfckyf';
                const token = Buffer.from(`${username}:${password}`, 'utf8').toString('base64');
                proxyReq.setHeader('Authorization', `Basic ${token}`);
            }
        },
    },
});
