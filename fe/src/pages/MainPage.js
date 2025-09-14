import React, { useState, useEffect } from 'react';
import { 
  Layout, 
  Tabs, 
  Button, 
  Typography, 
  Space, 
  Avatar, 
  Dropdown,
  message,
  Breadcrumb 
} from 'antd';
import { 
  FileTextFilled, 
  UploadOutlined,
  DatabaseOutlined,
  MessageFilled, 
  UserOutlined, 
  LogoutOutlined,
  SettingFilled,
  HomeOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import DocumentManagement from '../components/DocumentManagement';
import DocumentUpload from '../components/DocumentUpload';
import ChunksViewer from '../components/ChunksViewer';
import ChatBot from '../components/ChatBot';
import logo from '../assets/logo.png';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const MainPage = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('documents');

  // Breadcrumb configuration
  const getBreadcrumbItems = () => {
    const baseItems = [
      {
        href: '/',
        title: (
          <Space>
            <HomeOutlined />
            <span>Trang chủ</span>
          </Space>
        ),
      }
    ];

    switch (activeTab) {
      case 'documents':
        return [...baseItems, {
          title: (
            <Space>
              <FileTextFilled />
              <span>Quản lý Tài liệu</span>
            </Space>
          ),
        }];
      case 'upload':
        return [...baseItems, {
          title: (
            <Space>
              <UploadOutlined />
              <span>Tải lên Tài liệu</span>
            </Space>
          ),
        }];
      case 'chunks':
        return [...baseItems, {
          title: (
            <Space>
              <DatabaseOutlined />
              <span>Vector Chunks</span>
            </Space>
          ),
        }];
      case 'chat':
        return [...baseItems, {
          title: (
            <Space>
              <MessageFilled />
              <span>Hỗ trợ Trực tuyến</span>
            </Space>
          ),
        }];
      default:
        return baseItems;
    }
  };

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
      icon: <SettingFilled style={{ color: '#D2691E' }} />,
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
          <FileTextFilled style={{ padding: '2px', background: 'rgba(210, 105, 30, 0.1)', borderRadius: '4px' }} />
          Quản lý Tài liệu
        </span>
      ),
      children: <DocumentManagement />
    },
    {
      key: 'upload',
      label: (
        <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <UploadOutlined style={{ padding: '2px', background: 'rgba(210, 105, 30, 0.1)', borderRadius: '4px' }} />
          Tải lên Tài liệu
        </span>
      ),
      children: <DocumentUpload />
    },
    {
      key: 'chunks',
      label: (
        <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <DatabaseOutlined style={{ padding: '2px', background: 'rgba(210, 105, 30, 0.1)', borderRadius: '4px' }} />
          Vector Chunks
        </span>
      ),
      children: <ChunksViewer />
    },
    {
      key: 'chatbot',
      label: (
        <span style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <MessageFilled style={{ padding: '2px', background: 'rgba(210, 105, 30, 0.1)', borderRadius: '4px' }} />
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
              src={logo} 
              alt="DVC.AI Logo" 
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
                    borderRadius: '12px',
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
                      color: '#6B3410',
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
        {/* Breadcrumb Navigation */}
        <div style={{ 
          maxWidth: '1600px',
          margin: '0 auto',
          marginBottom: 'clamp(12px, 2vw, 16px)'
        }}>
          <Breadcrumb
            items={getBreadcrumbItems()}
            style={{
              padding: 'clamp(8px, 2vw, 12px) clamp(12px, 3vw, 16px)',
              background: 'rgba(255, 255, 255, 0.9)',
              borderRadius: 'clamp(8px, 1.5vw, 12px)',
              border: '1px solid rgba(210, 105, 30, 0.1)',
              fontSize: 'clamp(13px, 2.5vw, 14px)',
              fontFamily: "'MaisonNeue', 'Inter', sans-serif",
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)'
            }}
            separator={
              <span style={{ 
                color: '#D2691E', 
                fontWeight: '500',
                margin: '0 4px'
              }}>
                /
              </span>
            }
          />
        </div>

        <div style={{ 
          background: 'white', 
          borderRadius: 'clamp(10px, 1.5vw, 16px)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
          overflow: 'hidden',
          maxWidth: '1600px',
          margin: '0 auto',
          minHeight: 'calc(100vh - clamp(160px, 24vw, 208px))'
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
