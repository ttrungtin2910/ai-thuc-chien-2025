import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Avatar,
  List,
  Empty,
  Spin,
  Divider,
  Tag
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  ReloadOutlined,
  MessageOutlined
} from '@ant-design/icons';
import { chatbotAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import moment from 'moment';

const { Title, Text } = Typography;
const { TextArea } = Input;

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Welcome message
    const welcomeMessage = {
      id: 1,
      type: 'bot',
      content: 'Xin chào! Tôi là trợ lý ảo của hệ thống quản lý tài liệu. Tôi có thể giúp bạn:\n\n• Hướng dẫn sử dụng hệ thống\n• Giải đáp thắc mắc về tài liệu\n• Hỗ trợ kỹ thuật cơ bản\n\nBạn cần hỗ trợ gì ạ?',
      timestamp: new Date().toISOString(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await chatbotAPI.sendMessage(inputMessage);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.response,
        timestamp: response.timestamp,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau hoặc liên hệ với bộ phận hỗ trợ.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    const welcomeMessage = {
      id: 1,
      type: 'bot',
      content: 'Cuộc trò chuyện đã được xóa. Bạn cần hỗ trợ gì ạ?',
      timestamp: new Date().toISOString(),
    };
    setMessages([welcomeMessage]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickQuestions = [
    'Làm thế nào để tải lên tài liệu?',
    'Các định dạng file nào được hỗ trợ?',
    'Làm sao để xóa tài liệu?',
    'Hệ thống có giới hạn dung lượng file không?'
  ];

  const MessageItem = ({ message }) => (
    <div style={{
      display: 'flex',
      justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
      marginBottom: 'clamp(12px, 2vw, 16px)'
    }}>
      <div style={{
        display: 'flex',
        flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
        maxWidth: window.innerWidth <= 768 ? '90%' : 'clamp(70%, 15vw, 80%)',
        gap: 'clamp(6px, 1.5vw, 12px)'
      }}>
        <Avatar
          size={window.innerWidth <= 768 ? 'small' : 'default'}
          icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
          style={{
            backgroundColor: message.type === 'user' ? '#D2691E' : '#52c41a',
            flexShrink: 0
          }}
        />
        
        <div style={{
          background: message.type === 'user' ? '#D2691E' : (message.isError ? '#fff2f0' : '#f6ffed'),
          color: message.type === 'user' ? 'white' : (message.isError ? '#a8071a' : '#389e0d'),
          padding: 'clamp(8px, 2vw, 12px) clamp(12px, 3vw, 16px)',
          borderRadius: 'clamp(8px, 2vw, 16px)',
          border: message.isError ? '1px solid #ffccc7' : '1px solid transparent',
          maxWidth: '100%',
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap',
          fontSize: 'clamp(13px, 2.5vw, 14px)',
          lineHeight: '1.5',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          transition: 'all 0.2s ease'
        }}>
          <div>{message.content}</div>
          <div style={{
            fontSize: 'clamp(10px, 2vw, 11px)',
            opacity: 0.7,
            marginTop: '6px',
            textAlign: message.type === 'user' ? 'right' : 'left'
          }}>
            {moment(message.timestamp).format('HH:mm')}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div 
      style={{ 
        padding: 'clamp(16px, 3vw, 24px)',
        display: 'flex', 
        flexDirection: 'column',
        minHeight: '600px',
        overflow: 'auto'
      }}
    >
      <div className="mb-4">
        <Title 
          level={3} 
          className="mb-1 lh-tight font-semibold" 
          style={{ 
            color: '#D2691E', 
            fontFamily: "'MaisonNeue', 'Inter', sans-serif",
            fontSize: 'clamp(20px, 4vw, 28px)'
          }}
        >
          Hỗ trợ Trực tuyến
        </Title>
        <Text type="secondary" className="text-base lh-relaxed" style={{ fontSize: 'clamp(14px, 2.5vw, 16px)' }}>
          Trò chuyện với trợ lý ảo DVC.AI để được hỗ trợ nhanh chóng
        </Text>
      </div>

      <div style={{ 
        display: 'flex', 
        gap: 'clamp(12px, 3vw, 24px)', 
        flex: 1,
        flexDirection: window.innerWidth <= 992 ? 'column' : 'row',
        minHeight: 0
      }}>
        {/* Chat Area */}
        <Card 
          style={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column',
            minHeight: window.innerWidth <= 992 ? '400px' : 'auto'
          }}
          bodyStyle={{ 
            display: 'flex', 
            flexDirection: 'column', 
            padding: 0, 
            height: '100%',
            minHeight: 0
          }}
        >
          {/* Chat Header */}
          <div style={{
            padding: '16px 24px',
            borderBottom: '1px solid #f0f0f0',
            background: '#fafafa'
          }}>
            <Space>
              <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} />
              <div>
                <Text strong>Trợ lý ảo</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  <Tag color="green" size="small">Trực tuyến</Tag>
                </Text>
              </div>
            </Space>
            
            <Button
              icon={<ReloadOutlined />}
              size="small"
              type="text"
              onClick={clearChat}
              style={{ float: 'right' }}
            >
              Xóa cuộc trò chuyện
            </Button>
          </div>

          {/* Messages */}
          <div style={{
            flex: 1,
            padding: '16px 24px',
            overflowY: 'auto',
            background: '#fafafa'
          }}>
            {messages.length === 0 ? (
              <Empty
                description="Chưa có tin nhắn"
                image={Empty.PRESENTED_IMAGE_SIMPLE}
              />
            ) : (
              <>
                {messages.map((message) => (
                  <MessageItem key={message.id} message={message} />
                ))}
                {loading && (
                  <div style={{ textAlign: 'center', margin: '16px 0' }}>
                    <Spin size="small" />
                    <Text type="secondary" style={{ marginLeft: '8px' }}>
                      Đang trả lời...
                    </Text>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input Area */}
          <div style={{
            padding: 'clamp(12px, 3vw, 16px) clamp(16px, 4vw, 24px)',
            borderTop: '2px solid #f0f0f0',
            background: 'linear-gradient(135deg, #fafafa 0%, #ffffff 100%)'
          }}>
            <div style={{ 
              display: 'flex',
              gap: 'clamp(8px, 2vw, 12px)',
              alignItems: 'flex-end'
            }}>
              <TextArea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Nhập tin nhắn của bạn..."
                autoSize={{ minRows: 1, maxRows: window.innerWidth <= 768 ? 3 : 4 }}
                style={{ 
                  flex: 1,
                  borderRadius: 'clamp(8px, 2vw, 12px)',
                  fontSize: 'clamp(13px, 2.5vw, 14px)',
                  transition: 'all 0.3s ease'
                }}
                disabled={loading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={sendMessage}
                loading={loading}
                disabled={!inputMessage.trim()}
                className="btn-government"
                style={{ 
                  height: 'auto',
                  minHeight: 'clamp(36px, 8vw, 44px)',
                  borderRadius: 'clamp(8px, 2vw, 12px)',
                  fontSize: 'clamp(12px, 2.5vw, 14px)',
                  padding: 'clamp(8px, 2vw, 12px) clamp(12px, 3vw, 16px)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              />
            </div>
          </div>
        </Card>

        {/* Quick Actions */}
        <Card
          title="Câu hỏi thường gặp"
          style={{ 
            width: window.innerWidth <= 992 ? '100%' : 'clamp(280px, 25vw, 350px)',
            minHeight: window.innerWidth <= 992 ? 'auto' : '300px'
          }}
          size="small"
        >
          <Space direction="vertical" style={{ width: '100%' }} size="small">
            {quickQuestions.map((question, index) => (
              <Button
                key={index}
                type="text"
                size="small"
                onClick={() => setInputMessage(question)}
                style={{
                  height: 'auto',
                  padding: '8px 12px',
                  textAlign: 'left',
                  whiteSpace: 'normal',
                  border: '1px solid #f0f0f0',
                  borderRadius: '6px'
                }}
                block
              >
                <MessageOutlined style={{ marginRight: '8px', color: '#D2691E' }} />
                {question}
              </Button>
            ))}
          </Space>

          <Divider />

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Cần hỗ trợ thêm?<br />
              Liên hệ: support@domain.gov.vn<br />
              Hotline: 1900-xxxx
            </Text>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ChatBot;
