import axios from 'axios';
import { message } from 'antd';

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
