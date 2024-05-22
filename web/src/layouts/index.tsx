import React from 'react';
import { Layout, Menu, Button, ConfigProvider, theme } from 'antd';
import { history, Outlet, useLocation } from 'umi';

import enUS from "antd/locale/en_US";

const { Header, Content, Footer } = Layout;

const menuItems = [
    { key: '/', label: 'Downloader' },
    { key: '/file', label: 'Files' },
    { key: '/play', label: 'Play' },
]

const App: React.FC = () => {
    const location = useLocation();
    const {
        token: { colorBgContainer, borderRadiusLG },
    } = theme.useToken();

    return (
        <ConfigProvider locale={enUS}>
            <Layout>
                <Header
                    style={{
                        position: 'sticky',
                        top: 0,
                        zIndex: 1,
                        width: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        background: '#fff'
                    }}
                >
                    <h2>RoboMaster Live Capture</h2>
                    <Menu
                        mode="horizontal"
                        selectedKeys={[location.pathname]}
                        items={menuItems}
                        style={{ flex: 1, minWidth: 0, paddingLeft: 40 }}
                        onClick={({ key }) => history.push(key)}
                    />
                </Header>
                <Content style={{ padding: "24px 24px 0 24px" }}>
                    <div
                        style={{
                            padding: 24,
                            minHeight: "calc(100vh - 160px)",
                            background: colorBgContainer,
                            borderRadius: borderRadiusLG,
                        }}
                    >
                        <Outlet />
                    </div>
                </Content>
                <Footer style={{ textAlign: 'center' }}>
                    Created by&nbsp;
                    <a href="https://github.com/bismarckkk" target="_blank">
                        <Button type="link" style={{padding: 0}} size="small">
                            Bismarckkk
                        </Button>
                    </a>
                </Footer>
            </Layout>
        </ConfigProvider>
    );
};

export default App;
