import React, { useState, useEffect } from 'react';
import { 
  Layout, 
  Tabs, 
  Button, 
  Typography, 
  Space, 
  Avatar, 
  Dropdown,
  message 
} from 'antd';
import { 
  FileTextOutlined, 
  MessageOutlined, 
  UserOutlined, 
  LogoutOutlined,
  SettingOutlined,
  CloudUploadOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import DocumentManagement from '../components/DocumentManagement';
import ChatBot from '../components/ChatBot';
import BulkUpload from '../components/BulkUpload';
import dongsondrum from '../assets/dongson-drum.svg';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const MainPage = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('documents');

  const handleLogout = () => {
    logout();
    message.success('Đăng xuất thành công!');
  };

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Thông tin cá nhân',
      onClick: () => message.info('Tính năng đang phát triển')
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Cài đặt',
      onClick: () => message.info('Tính năng đang phát triển')
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Đăng xuất',
      onClick: handleLogout
    },
  ];

  const tabItems = [
    {
      key: 'documents',
              label: (
          <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <FileTextOutlined />
            Quản lý Tài liệu
          </span>
        ),
      children: <DocumentManagement />
    },
    {
      key: 'bulk-upload',
              label: (
          <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <CloudUploadOutlined />
            Upload Đồng loạt
          </span>
        ),
      children: <BulkUpload />
    },
    {
      key: 'chatbot',
              label: (
          <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <MessageOutlined />
            Hỗ trợ Trực tuyến
          </span>
        ),
      children: <ChatBot />
    }
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className="government-header" style={{ height: '80px' }}>
        <div className="header-content" style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: '0 clamp(16px, 4vw, 32px)',
          maxWidth: '1600px',
          margin: '0 auto',
          width: '100%',
          height: '80px'
        }}>
          <div className="icon-text-gap-lg" style={{ minWidth: 0, flex: '1 1 auto' }}>
            <img 
              src={dongsondrum} 
              alt="Trống đồng Đông Sơn" 
              style={{ 
                width: 'clamp(32px, 5vw, 40px)', 
                height: 'clamp(32px, 5vw, 40px)', 
                filter: 'brightness(0) invert(1)',
                flexShrink: 0
              }}
            />
            <div style={{ minWidth: 0 }}>
              <Title 
                level={3} 
                className="mb-0 lh-tight" 
                style={{ 
                  color: '#ffffff', 
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif",
                  fontSize: 'clamp(18px, 4vw, 24px)',
                  margin: 0,
                  textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
                  fontWeight: '700'
                }}
              >
                DVC.AI
              </Title>
              <Text 
                className="text-sm lh-normal hidden-xs" 
                style={{ 
                  color: 'rgba(255, 255, 255, 0.9)', 
                  display: 'block',
                  marginTop: '2px',
                  fontSize: 'clamp(12px, 2.5vw, 14px)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
                }}
              >
                Trợ lý dịch vụ công và cổng Kiến thức
              </Text>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 'clamp(12px, 3vw, 20px)', flexShrink: 0 }}>
            <Text 
              className="hidden-xs" 
              style={{ 
                color: 'rgba(255, 255, 255, 0.9)',
                fontSize: 'clamp(12px, 2.5vw, 14px)',
                textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)',
                fontWeight: '500'
              }}
            >
              Xin chào,
            </Text>
            <Dropdown 
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              trigger={['click']}
            >
                              <Button 
                  type="text" 
                  className="icon-text-gap-sm user-dropdown-btn"
                  style={{ 
                    color: '#ffffff', 
                    height: 'auto',
                    padding: 'clamp(4px, 1vw, 8px) clamp(8px, 2vw, 12px)',
                    borderRadius: '8px',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    border: '1px solid rgba(255, 255, 255, 0.3)',
                    fontSize: 'clamp(12px, 2.5vw, 14px)',
                    backgroundColor: 'rgba(255, 255, 255, 0.15)',
                    textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)'
                  }}
                >
                                  <Avatar 
                    size={window.innerWidth <= 768 ? 'small' : 'default'} 
                    icon={<UserOutlined />} 
                    style={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.25)',
                      color: '#8B4513',
                      flexShrink: 0,
                      border: '1px solid rgba(255, 255, 255, 0.3)'
                    }}
                  />
                  <span className="font-medium hidden-xs" style={{ 
                    whiteSpace: 'nowrap', 
                    overflow: 'hidden', 
                    textOverflow: 'ellipsis', 
                    maxWidth: '120px',
                    textShadow: '0 1px 2px rgba(0, 0, 0, 0.2)',
                    fontWeight: '600'
                  }}>
                    {user?.full_name || user?.username}
                  </span>
              </Button>
            </Dropdown>
          </div>
        </div>
      </Header>

      <Content style={{ 
        padding: 'clamp(16px, 3vw, 24px)', 
        background: '#f5f7fa',
        minHeight: 'calc(100vh - 80px)'
      }}>
        <div style={{ 
          background: 'white', 
          borderRadius: 'clamp(6px, 1.5vw, 12px)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          overflow: 'hidden',
          maxWidth: '1600px',
          margin: '0 auto',
          minHeight: 'calc(100vh - clamp(128px, 20vw, 176px))'
        }}>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={tabItems}
            size="large"
            className="government-tabs"
            style={{ 
              margin: 0
            }}
            tabBarStyle={{
              margin: 0,
              padding: '0 clamp(16px, 3vw, 24px)',
              background: 'linear-gradient(135deg, #fafbfc 0%, #f8f9fa 100%)',
              borderBottom: '2px solid #e8e8e8'
            }}
          />
        </div>
      </Content>
    </Layout>
  );
};

export default MainPage;
