import React, { useState } from 'react';
import { Form, Input, Button, message, Card, Typography, Space } from 'antd';
import { UserOutlined, LockFilled, SafetyOutlined } from '@ant-design/icons';
import logo from '../assets/logo.png';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const result = await login(values);
      if (result.success) {
        message.success('Đăng nhập thành công!');
        navigate('/');
      } else {
        message.error(result.error);
      }
    } catch (error) {
      message.error('Có lỗi xảy ra, vui lòng thử lại!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Card className="login-box" style={{ 
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
        maxWidth: window.innerWidth <= 768 ? 'calc(100vw - 32px)' : '400px',
        margin: window.innerWidth <= 768 ? '16px' : '0'
      }}>
        <div className="login-logo">
          <Space direction="vertical" align="center" size="small">
            <img 
              src={logo} 
              alt="DVC.AI Logo" 
              style={{ 
                width: window.innerWidth <= 480 ? '48px' : '64px', 
                height: window.innerWidth <= 480 ? '48px' : '64px' 
              }}
            />
            <Title level={2} style={{ 
              margin: 0, 
              color: '#D2691E', 
              fontFamily: "'MaisonNeue', 'Inter', sans-serif",
              fontSize: window.innerWidth <= 480 ? '20px' : '28px'
            }}>
              DVC.AI
            </Title>
            <Text type="secondary" style={{
              fontSize: window.innerWidth <= 480 ? '13px' : '14px',
              textAlign: 'center'
            }}>
              Trợ lý dịch vụ công và cổng Kiến thức
            </Text>
          </Space>
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size={window.innerWidth <= 480 ? 'middle' : 'large'}
          style={{ marginTop: window.innerWidth <= 480 ? '24px' : '32px' }}
        >
          <Form.Item
            label={<span style={{ fontSize: window.innerWidth <= 480 ? '14px' : '16px' }}>Tên đăng nhập</span>}
            name="username"
            rules={[
              {
                required: true,
                message: 'Vui lòng nhập tên đăng nhập!',
              },
            ]}
          >
            <Input 
              prefix={<UserOutlined style={{ color: '#D2691E' }} />} 
              placeholder="Nhập tên đăng nhập"
              style={{ 
                borderRadius: '10px',
                fontSize: window.innerWidth <= 480 ? '14px' : '16px',
                height: window.innerWidth <= 480 ? '40px' : 'auto'
              }}
            />
          </Form.Item>

          <Form.Item
            label={<span style={{ fontSize: window.innerWidth <= 480 ? '14px' : '16px' }}>Mật khẩu</span>}
            name="password"
            rules={[
              {
                required: true,
                message: 'Vui lòng nhập mật khẩu!',
              },
            ]}
          >
            <Input.Password
              prefix={<LockFilled style={{ color: '#D2691E' }} />}
              placeholder="Nhập mật khẩu"
              style={{ 
                borderRadius: '10px',
                fontSize: window.innerWidth <= 480 ? '14px' : '16px',
                height: window.innerWidth <= 480 ? '40px' : 'auto'
              }}
            />
          </Form.Item>

          <Form.Item style={{ marginTop: window.innerWidth <= 480 ? '24px' : '32px', marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              className="btn-government"
              style={{ 
                height: window.innerWidth <= 480 ? '44px' : '48px', 
                fontSize: window.innerWidth <= 480 ? '15px' : '16px',
                fontWeight: '600',
                borderRadius: window.innerWidth <= 480 ? '10px' : '12px'
              }}
            >
              Đăng nhập
            </Button>
          </Form.Item>
        </Form>

        <div style={{ 
          marginTop: window.innerWidth <= 480 ? '20px' : '24px', 
          padding: window.innerWidth <= 480 ? '12px' : '16px', 
          background: '#f8f9fa', 
          borderRadius: window.innerWidth <= 480 ? '10px' : '12px',
          border: '1px solid #dee2e6'
        }}>
          <Text type="secondary" style={{ fontSize: window.innerWidth <= 480 ? '12px' : '13px' }}>
            <strong>Tài khoản demo:</strong><br />
            Tên đăng nhập: <code style={{ fontSize: window.innerWidth <= 480 ? '11px' : '12px' }}>admin</code><br />
            Mật khẩu: <code style={{ fontSize: window.innerWidth <= 480 ? '11px' : '12px' }}>password123</code>
          </Text>
        </div>

        <div style={{ textAlign: 'center', marginTop: window.innerWidth <= 480 ? '20px' : '24px' }}>
          <Text type="secondary" style={{ fontSize: window.innerWidth <= 480 ? '11px' : '12px' }}>
            2025 DVC.ai
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;
