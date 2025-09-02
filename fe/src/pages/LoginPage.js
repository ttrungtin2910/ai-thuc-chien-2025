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
      <Card className="login-box" style={{ boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)' }}>
        <div className="login-logo">
          <Space direction="vertical" align="center" size="small">
            <img 
              src={logo} 
              alt="DVC.AI Logo" 
              style={{ width: '64px', height: '64px' }}
            />
            <Title level={2} style={{ margin: 0, color: '#D2691E', fontFamily: "'MaisonNeue', 'Inter', sans-serif" }}>
              DVC.AI
            </Title>
            <Text type="secondary">
              Trợ lý dịch vụ công và cổng Kiến thức
            </Text>
          </Space>
        </div>

        <Form
          name="login"
          onFinish={onFinish}
          layout="vertical"
          size="large"
          style={{ marginTop: '32px' }}
        >
          <Form.Item
            label="Tên đăng nhập"
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
              style={{ borderRadius: '10px' }}
            />
          </Form.Item>

          <Form.Item
            label="Mật khẩu"
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
              style={{ borderRadius: '10px' }}
            />
          </Form.Item>

          <Form.Item style={{ marginTop: '32px', marginBottom: 0 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              className="btn-government"
              style={{ 
                height: '48px', 
                fontSize: '16px',
                fontWeight: '600',
                borderRadius: '12px'
              }}
            >
              Đăng nhập
            </Button>
          </Form.Item>
        </Form>

        <div style={{ 
          marginTop: '24px', 
          padding: '16px', 
          background: '#f8f9fa', 
          borderRadius: '12px',
          border: '1px solid #dee2e6'
        }}>
          <Text type="secondary" style={{ fontSize: '13px' }}>
            <strong>Tài khoản demo:</strong><br />
            Tên đăng nhập: <code>admin</code><br />
            Mật khẩu: <code>password123</code>
          </Text>
        </div>

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            © 2024 Hệ thống Quản lý Tài liệu. Phiên bản 1.0.0
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default LoginPage;
