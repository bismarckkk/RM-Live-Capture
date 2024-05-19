import axios from 'axios';
import { message } from 'antd';

if (process.env.NODE_ENV === 'development') {
    const username = 'nuaanuaa';
    const password = 'ckyfckyf';
    const token = Buffer.from(`${username}:${password}`, 'utf8').toString('base64');
    axios.defaults.headers.common['Authorization'] = `Basic ${token}`;
}

axios.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        console.error(error);
        message.error(error.message);
        return Promise.reject(error);
    }
);
