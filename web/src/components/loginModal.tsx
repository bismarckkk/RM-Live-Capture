import React, {Component} from 'react';
import { Modal, Result } from "antd";
import Loading from "@/loading";
import axios from "axios";
import {ApiResult} from "@/utils";

interface LoginApiResult {
    code: number;
    qr: string;
    key: string;
}


class LoginModal extends Component {
    state = { open: false, t: -1 }
    qrCode = '';
    key = '';
    timer: NodeJS.Timeout | null = null;

    async open() {
        this.setState({open: true})
        const res = await axios.get<LoginApiResult>(`/api/bili/login`)
        this.qrCode = res.data.qr;
        this.key = res.data.key;
        this.timer = setInterval(async () => {
            await this.check();
        }, 1500);
        this.setState({t: 0})
    }

    componentWillUnmount() {
        if (this.timer) {
            clearInterval(this.timer);
        }
    }

    async check() {
        if (!this.state.open) {
            clearInterval(this.timer!);
            this.timer = null;
        }
        const res = await axios.get<ApiResult>(`/api/bili/check?key=${this.key}`);
        if (res.data.code !== 0) {
            clearInterval(this.timer!);
            this.timer = null;
            this.setState({t: res.data.code})
            setTimeout(() => {
                this.setState({open: false})
            }, 3000)
        }
    }

    render() {
        let res = <Loading />;
        if (this.state.t === 0) {
            res = <div style={{textAlign: 'center', width: '100%'}}>
                <img src={this.qrCode} alt="qrCode" style={{width: '100%', height: 'auto'}} />
            </div>
        } else if (this.state.t === 1) {
            res = <Result
                status="error"
                title="QrCode Timeout!"
            />
        } else if (this.state.t === 1000) {
            res = <Result
                status="success"
                title="Login Success!"
            />
        }
        return (
            <Modal
                open={this.state.open}
                footer={null}
                onCancel={() => this.setState({open: false})}
                title="BiliBili Login"
            >
                {res}
            </Modal>
        );
    }
}

export default LoginModal;
