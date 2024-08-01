import React, {Component} from 'react';
import { ModalForm, ProFormText } from "@ant-design/pro-components";

class FormModal extends Component {
    state = {title: '', open: false}
    promise ?: {resolve: Function, reject: Function} = undefined

    open(title: string) {
        return new Promise<string>((resolve, reject) => {
            this.setState({title, open: true})
            if (this.promise) {
                this.promise.reject()
            }
            this.promise = {resolve, reject}
        })
    }

    render() {
        return (
            <ModalForm
                title={this.state.title}
                autoFocusFirstInput
                width={500}
                open={this.state.open}
                onOpenChange={(e)=>{
                    if (this.promise && !e && this.state.open) {
                        this.promise.reject()
                    }
                    this.setState({open: e})
                }}
                onFinish={async (e)=>{
                    this?.promise?.resolve(e.title)
                    this.promise = undefined
                    return true
                }}
            >
                <ProFormText
                    name="title"
                    label="Video Title"
                    width="lg"
                    rules={[
                        { required: true },
                    ]}
                />
            </ModalForm>
        );
    }
}

export default FormModal;