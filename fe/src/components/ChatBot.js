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
  Tag,
  Modal,
  Descriptions
} from 'antd';
import {
  SendOutlined,
  RobotFilled,
  UserOutlined,
  ReloadOutlined,
  MessageFilled,
  FileTextOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { chatbotAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import websocketService from '../services/websocket';
import moment from 'moment';

const { Title, Text } = Typography;
const { TextArea } = Input;

const ChatBot = React.memo(() => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [typing, setTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const [useWebSocket, setUseWebSocket] = useState(true);
  const [sourcesModalVisible, setSourcesModalVisible] = useState(false);
  const [selectedSources, setSelectedSources] = useState([]);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize session ID
    const newSessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);

    // Welcome message with Markdown formatting
    const welcomeMessage = {
      id: 1,
      type: 'bot',
      content: `# Xin chào! 👋

Tôi là **DVC.AI**, trợ lý ảo thông minh chuyên về dịch vụ công và thủ tục hành chính Việt Nam.

## 🔍 Tôi có thể giúp bạn:

- **Tìm kiếm thông tin** về thủ tục hành chính
- **Hướng dẫn quy trình** làm giấy tờ
- **Tư vấn về hồ sơ** và yêu cầu
- **Trả lời các câu hỏi** về dịch vụ công

> Bạn có câu hỏi gì về thủ tục hành chính không? 🤔`,
      timestamp: new Date().toISOString(),
    };
    setMessages([welcomeMessage]);

    return () => {
      cleanupWebSocket();
    };
  }, [user]);

  // Separate effect for WebSocket setup after sessionId is set
  useEffect(() => {
    if (user?.username && sessionId) {
      setupWebSocket();
    }
  }, [user, sessionId]);

  const setupWebSocket = () => {
    try {
      // Connect to WebSocket
      websocketService.connect(user.username);

      // Set up event listeners
      websocketService.on('connection_status', handleConnectionStatus);
      websocketService.on('chat_response', handleChatResponse);
      websocketService.on('typing', handleTyping);
      websocketService.on('error', handleWebSocketError);

      // Join chat session when connected
      const connectHandler = (data) => {
        if (data.connected && sessionId) {
          websocketService.joinChatSession(sessionId);
        }
      };

      websocketService.on('connection_status', connectHandler);

    } catch (error) {
      console.error('Failed to setup WebSocket:', error);
      setUseWebSocket(false);
    }
  };

  const cleanupWebSocket = () => {
    if (sessionId) {
      websocketService.leaveChatSession(sessionId);
    }
    websocketService.off('connection_status', handleConnectionStatus);
    websocketService.off('chat_response', handleChatResponse);
    websocketService.off('typing', handleTyping);
    websocketService.off('error', handleWebSocketError);
  };

  const handleConnectionStatus = (data) => {
    setIsWebSocketConnected(data.connected);
    if (data.connected && sessionId) {
      websocketService.joinChatSession(sessionId);
    }
  };

  const handleChatResponse = (data) => {
    if (data.session_id !== sessionId) return;

    const botMessage = {
      id: Date.now(),
      type: 'bot',
      content: data.response,
      timestamp: data.timestamp,
      metadata: data.metadata
    };

    setMessages(prev => [...prev, botMessage]);
    setLoading(false);
    setTyping(false);
  };

  const handleTyping = (data) => {
    if (data.session_id !== sessionId) return;
    setTyping(data.typing);
  };

  const handleWebSocketError = (data) => {
    const errorMessage = {
      id: Date.now(),
      type: 'bot',
      content: data.message || 'Có lỗi xảy ra trong quá trình xử lý.',
      timestamp: new Date().toISOString(),
      isError: true,
    };
    setMessages(prev => [...prev, errorMessage]);
    setLoading(false);
    setTyping(false);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    const messageText = inputMessage;
    setInputMessage('');
    setLoading(true);

    try {
      if (useWebSocket && isWebSocketConnected && sessionId) {
        // Use WebSocket for real-time communication
        websocketService.sendChatMessage(messageText, sessionId);
      } else {
        // Fall back to HTTP API
        const response = await chatbotAPI.sendMessage({
          message: messageText,
          session_id: sessionId
        });
        
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: response.response,
          timestamp: response.timestamp,
          metadata: response.metadata
        };

        setMessages(prev => [...prev, botMessage]);
        setLoading(false);
      }
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại sau hoặc liên hệ với bộ phận hỗ trợ.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      setMessages(prev => [...prev, errorMessage]);
      setLoading(false);
    }
  };

  const clearChat = () => {
    // Generate new session ID for fresh conversation
    const newSessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);

    // Leave old session and join new one
    if (isWebSocketConnected) {
      websocketService.joinChatSession(newSessionId);
    }

    const welcomeMessage = {
      id: 1,
      type: 'bot',
      content: `## 🔄 Cuộc trò chuyện mới đã được bắt đầu!

Tôi là **DVC.AI**, sẵn sàng hỗ trợ bạn về các thủ tục hành chính.

> Bạn có câu hỏi gì không? 😊`,
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
    'Thủ tục làm căn cước công dân như thế nào?',
    'Cần những giấy tờ gì để đăng ký thường trú?',
    'Quy trình xin cấp hộ chiếu mới?',
    'Thời gian xử lý hồ sơ là bao lâu?',
    'Lệ phí các thủ tục hành chính?',
    'Địa điểm nộp hồ sơ ở đâu?'
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
          icon={message.type === 'user' ? <UserOutlined /> : <RobotFilled />}
          style={{
            backgroundColor: message.type === 'user' ? '#D2691E' : '#52c41a',
            flexShrink: 0,
            border: '2px solid rgba(255, 255, 255, 0.8)'
          }}
        />
        
        <div style={{
          background: message.type === 'user' ? '#D2691E' : (message.isError ? '#fff2f0' : '#f6ffed'),
          color: message.type === 'user' ? 'white' : (message.isError ? '#a8071a' : '#389e0d'),
          padding: 'clamp(8px, 2vw, 12px) clamp(12px, 3vw, 16px)',
          borderRadius: 'clamp(12px, 2vw, 18px)',
          border: message.isError ? '1px solid #ffccc7' : '1px solid transparent',
          maxWidth: '100%',
          wordBreak: 'break-word',
          whiteSpace: message.type === 'user' ? 'pre-wrap' : 'normal',
          fontSize: 'clamp(13px, 2.5vw, 14px)',
          lineHeight: '1.5',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          transition: 'all 0.2s ease'
        }}>
          <div className={message.type === 'bot' ? 'bot-message-content' : ''}>
            {message.type === 'bot' ? (
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  // Custom styling for markdown elements
                  h1: ({children}) => <h1 style={{fontSize: '1.3em', fontWeight: 'bold', margin: '12px 0 8px 0', color: 'inherit'}}>{children}</h1>,
                  h2: ({children}) => <h2 style={{fontSize: '1.2em', fontWeight: 'bold', margin: '10px 0 6px 0', color: 'inherit'}}>{children}</h2>,
                  h3: ({children}) => <h3 style={{fontSize: '1.1em', fontWeight: 'bold', margin: '8px 0 4px 0', color: 'inherit'}}>{children}</h3>,
                  p: ({children}) => <p style={{margin: '4px 0', color: 'inherit'}}>{children}</p>,
                  ul: ({children}) => <ul style={{margin: '4px 0', paddingLeft: '20px', color: 'inherit'}}>{children}</ul>,
                  ol: ({children}) => <ol style={{margin: '4px 0', paddingLeft: '20px', color: 'inherit'}}>{children}</ol>,
                  li: ({children}) => <li style={{margin: '2px 0', color: 'inherit'}}>{children}</li>,
                  strong: ({children}) => <strong style={{fontWeight: 'bold', color: 'inherit'}}>{children}</strong>,
                  em: ({children}) => <em style={{fontStyle: 'italic', color: 'inherit'}}>{children}</em>,
                  code: ({children, ...props}) => {
                    return props.inline ? (
                      <code style={{
                        backgroundColor: 'rgba(0,0,0,0.1)', 
                        padding: '2px 4px', 
                        borderRadius: '3px',
                        fontSize: '0.9em',
                        color: 'inherit'
                      }}>
                        {children}
                      </code>
                    ) : (
                      <pre style={{
                        backgroundColor: 'rgba(0,0,0,0.1)', 
                        padding: '8px', 
                        borderRadius: '6px',
                        overflow: 'auto',
                        margin: '8px 0',
                        fontSize: '0.9em',
                        color: 'inherit'
                      }}>
                        <code>{children}</code>
                      </pre>
                    );
                  },
                  blockquote: ({children}) => (
                    <blockquote style={{
                      borderLeft: '3px solid rgba(0,0,0,0.2)',
                      paddingLeft: '12px',
                      margin: '8px 0',
                      fontStyle: 'italic',
                      color: 'inherit'
                    }}>
                      {children}
                    </blockquote>
                  )
                }}
              >
                {message.content}
              </ReactMarkdown>
            ) : (
              message.content
            )}
          </div>
          <div style={{
            fontSize: 'clamp(10px, 2vw, 11px)',
            opacity: 0.7,
            marginTop: '6px',
            textAlign: message.type === 'user' ? 'right' : 'left',
            display: 'flex',
            justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
            alignItems: 'center',
            gap: '4px'
          }}>
            {moment(message.timestamp).format('HH:mm')}
            {message.metadata && (
              <span style={{
                background: message.metadata.rag_used ? 'rgba(82, 196, 26, 0.1)' : 'rgba(64, 169, 255, 0.1)',
                color: message.metadata.rag_used ? '#52c41a' : '#40a9ff',
                padding: '1px 4px',
                borderRadius: '4px',
                fontSize: '10px'
              }}>
                {message.metadata.rag_used ? 'RAG' : 'NORMAL'}
              </span>
            )}
            {message.metadata?.sources?.length > 0 && (
              <span 
                style={{
                  background: 'rgba(24, 144, 255, 0.1)',
                  color: '#1890ff',
                  padding: '1px 4px',
                  borderRadius: '4px',
                  fontSize: '10px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onClick={() => {
                  setSelectedSources(message.metadata.sources);
                  setSourcesModalVisible(true);
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(24, 144, 255, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(24, 144, 255, 0.1)';
                }}
              >
                <InfoCircleOutlined style={{ marginRight: '2px' }} />
                {message.metadata.sources.length} nguồn
              </span>
            )}
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
        height: '100vh',
        overflow: 'hidden'
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
        overflow: 'hidden'
      }}>
        {/* Chat Area */}
        <Card 
          style={{ 
            flex: 1, 
            display: 'flex', 
            flexDirection: 'column',
            height: '100%'
          }}
          bodyStyle={{ 
            display: 'flex', 
            flexDirection: 'column', 
            padding: 0, 
            height: '100%',
            overflow: 'hidden'
          }}
        >
          {/* Chat Header */}
          <div style={{
            padding: '12px 20px',
            borderBottom: '1px solid #f0f0f0',
            background: '#fafafa',
            flexShrink: 0, // Prevent header from shrinking
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            minHeight: '50px'
          }}>
            <Space align="center" size="small">
              <Avatar 
                icon={<RobotFilled />} 
                size="small"
                style={{ 
                  backgroundColor: '#52c41a', 
                  border: '2px solid rgba(255, 255, 255, 0.8)'
                }} 
              />
              <div style={{ lineHeight: '1.2' }}>
                <Text 
                  strong 
                  style={{ 
                    fontFamily: "'MaisonNeue', 'Inter', sans-serif", 
                    fontSize: '14px',
                    color: '#333',
                    display: 'block',
                    marginBottom: '1px'
                  }}
                >
                  DVC.AI Trợ lý ảo
                </Text>
                <Tag 
                  color={isWebSocketConnected ? "green" : "orange"} 
                  size="small"
                  style={{ 
                    borderRadius: '6px',
                    fontSize: '10px',
                    padding: '0 4px',
                    lineHeight: '14px'
                  }}
                >
                  {isWebSocketConnected ? 'Trực tuyến' : 'Kết nối HTTP'}
                </Tag>
              </div>
            </Space>
            
            <Button
              icon={<ReloadOutlined />}
              size="small"
              type="text"
              onClick={clearChat}
              aria-label="Tạo cuộc trò chuyện mới"
              style={{ 
                borderRadius: '4px',
                color: '#D2691E',
                border: '1px solid rgba(210, 105, 30, 0.3)',
                padding: '2px 8px',
                height: '28px',
                fontSize: '12px',
                fontWeight: '500',
                background: 'rgba(210, 105, 30, 0.05)',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(210, 105, 30, 0.1)';
                e.target.style.borderColor = 'rgba(210, 105, 30, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(210, 105, 30, 0.05)';
                e.target.style.borderColor = 'rgba(210, 105, 30, 0.3)';
              }}
            >
              Tạo mới
            </Button>
          </div>

          {/* Messages */}
          <div 
            className="chat-messages-container"
            style={{
              flex: 1,
              padding: '16px 24px',
              overflowY: 'auto',
              overflowX: 'hidden',
              background: '#fafafa',
              flex: 1,
              minHeight: 0
            }}
          >
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
                {(loading || typing) && (
                  <div style={{ textAlign: 'center', margin: '16px 0' }}>
                    <Spin size="small" />
                    <Text type="secondary" style={{ marginLeft: '8px' }}>
                      {typing ? 'DVC.AI đang soạn tin...' : 'Đang xử lý...'}
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
            background: 'linear-gradient(135deg, #fafafa 0%, #ffffff 100%)',
            flexShrink: 0 // Prevent input area from shrinking
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
                  borderRadius: 'clamp(12px, 2vw, 16px)',
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
                aria-label="Gửi tin nhắn"
                style={{ 
                  height: 'auto',
                  minHeight: 'clamp(36px, 8vw, 44px)',
                  borderRadius: 'clamp(12px, 2vw, 16px)',
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
          title={
            <span style={{ fontFamily: "'MaisonNeue', 'Inter', sans-serif", color: '#D2691E' }}>
              Câu hỏi thường gặp
            </span>
          }
          style={{ 
            width: window.innerWidth <= 992 ? '100%' : 'clamp(280px, 25vw, 380px)',
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
                  borderRadius: '10px'
                }}
                block
              >
                <MessageFilled style={{ marginRight: '8px', color: '#D2691E', padding: '2px', background: 'rgba(210, 105, 30, 0.1)', borderRadius: '4px' }} />
                {question}
              </Button>
            ))}
          </Space>

          <Divider />

          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: '12px', fontFamily: "'MaisonNeue', 'Inter', sans-serif" }}>
              Trợ lý ảo DVC.AI sử dụng RAG và Langraph<br />
              <strong>Hỗ trợ 24/7:</strong> support@dvc.gov.vn<br />
              <strong>Hotline:</strong> 1900-xxxx
            </Text>
            {isWebSocketConnected && (
              <div style={{ marginTop: '8px' }}>
                <Tag color="green" size="small">
                  ⚡ Real-time Active
                </Tag>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Sources Detail Modal */}
      <Modal
        title={
          <Space>
            <FileTextOutlined style={{ color: '#1890ff' }} />
            <span>Chi tiết nguồn tài liệu</span>
          </Space>
        }
        open={sourcesModalVisible}
        onCancel={() => setSourcesModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setSourcesModalVisible(false)}>
            Đóng
          </Button>
        ]}
        width={800}
        style={{ top: 20 }}
      >
        <div style={{ maxHeight: '60vh', overflowY: 'auto' }}>
          {selectedSources.map((source, index) => (
            <Card
              key={index}
              size="small"
              style={{
                marginBottom: '16px',
                border: '1px solid #f0f0f0',
                borderRadius: '8px'
              }}
              title={
                <Space>
                  <FileTextOutlined style={{ color: '#52c41a' }} />
                  <Text strong style={{ color: '#D2691E' }}>
                    Nguồn {index + 1}: {source.title || source.file_name}
                  </Text>
                </Space>
              }
              extra={
                <Tag color="blue">
                  Độ liên quan: {(source.score * 100).toFixed(1)}%
                </Tag>
              }
            >
              <Descriptions
                column={1}
                size="small"
                bordered
                style={{ marginBottom: '12px' }}
              >
                <Descriptions.Item label="Tên file">
                  <Text code>{source.file_name}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="Phần/Mục">
                  <Text>{source.section || 'Không xác định'}</Text>
                </Descriptions.Item>
                <Descriptions.Item label="Độ tin cậy">
                  <Space>
                    <Text>{(source.score * 100).toFixed(2)}%</Text>
                    <Tag color={source.score > 0.8 ? 'green' : source.score > 0.6 ? 'orange' : 'red'}>
                      {source.score > 0.8 ? 'Cao' : source.score > 0.6 ? 'Trung bình' : 'Thấp'}
                    </Tag>
                  </Space>
                </Descriptions.Item>
              </Descriptions>
              
              <div>
                <Text strong style={{ color: '#666' }}>Nội dung trích xuất:</Text>
                <div style={{
                  background: '#f9f9f9',
                  padding: '12px',
                  borderRadius: '6px',
                  marginTop: '8px',
                  border: '1px solid #e8e8e8'
                }}>
                  <Text style={{ 
                    fontSize: '13px', 
                    lineHeight: '1.6',
                    color: '#333'
                  }}>
                    {source.content_preview || source.content || 'Không có nội dung preview'}
                  </Text>
                </div>
              </div>
            </Card>
          ))}
          
          {selectedSources.length === 0 && (
            <Empty description="Không có nguồn tài liệu nào" />
          )}
        </div>
      </Modal>
    </div>
  );
});

export default ChatBot;
