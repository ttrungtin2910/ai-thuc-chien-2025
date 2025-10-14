import React, { useState, useEffect } from 'react';
import useWindowSize from '../hooks/useWindowSize';
import {
  Button,
  Table,
  Space,
  Typography,
  message,
  Popconfirm,
  Card,
  Tag,
  Row,
  Col,
  Statistic,
  Empty,
  Spin,
  Progress,
  notification,
  Skeleton
} from 'antd';
import {
  DeleteFilled,
  FileTextFilled,
  FilePdfFilled,
  FileWordFilled,
  DownloadOutlined,
  ReloadOutlined,
  CheckCircleFilled,
  ExclamationCircleFilled
} from '@ant-design/icons';
import { documentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import websocketService from '../services/websocket';
import moment from 'moment';

const { Title, Text } = Typography;

const DocumentManagement = React.memo(() => {
  const { user } = useAuth();
  const { width } = useWindowSize();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  // Track file processing status for existing documents
  const [fileProcessingStatus, setFileProcessingStatus] = useState({});
  
  // Track when documents need to be refreshed
  const [needsRefresh, setNeedsRefresh] = useState(false);

  useEffect(() => {
    fetchDocuments();
    
    // Connect WebSocket if user is available
    if (user?.username && !websocketService.isSocketConnected()) {
      websocketService.connect(user.username);
    }
    
    // Additional handler for file processing updates
    const handleFileProcessing = (data) => {
      setFileProcessingStatus(prev => ({
        ...prev,
        [data.filename]: {
          progress: data.progress || 0,
          status: data.status || 'processing',
          task_id: data.task_id,
          timestamp: Date.now()
        }
      }));
    };

    const handleFileComplete = (data) => {
      // Clear file processing status
      setFileProcessingStatus(prev => {
        const newStatus = { ...prev };
        delete newStatus[data.filename];
        return newStatus;
      });
      
      // Trigger documents refresh
      setNeedsRefresh(true);
    };

    websocketService.on('file_processing_update', handleFileProcessing);
    websocketService.on('file_upload_complete', handleFileComplete);
    
    return () => {
      websocketService.off('file_processing_update', handleFileProcessing);
      websocketService.off('file_upload_complete', handleFileComplete);
    };
  }, [user?.username]);



  // Clean up old processing status periodically (không auto-refresh documents)
  useEffect(() => {
    const interval = setInterval(() => {
      // Clean up old processing status (older than 5 minutes)
      const fiveMinutesAgo = Date.now() - 5 * 60 * 1000;
      setFileProcessingStatus(prev => {
        const cleaned = {};
        Object.entries(prev).forEach(([filename, status]) => {
          if (status.timestamp > fiveMinutesAgo) {
            cleaned[filename] = status;
          }
        });
        return cleaned;
      });
    }, 30000); // Clean up every 30 seconds instead of 3 seconds

    return () => clearInterval(interval);
  }, []);

  // Refresh documents only when explicitly needed
  useEffect(() => {
    if (needsRefresh) {
      fetchDocuments();
      setNeedsRefresh(false);
    }
  }, [needsRefresh]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const data = await documentsAPI.getDocuments();
      setDocuments(data);
      
      // Không tự động đánh dấu files là processing khi reload
      // Chỉ dựa vào WebSocket events để update status
    } catch (error) {
      message.error('Không thể tải danh sách tài liệu');
      console.error('Fetch documents error:', error);
    } finally {
      setLoading(false);
    }
  };



  const handleDelete = async (documentId, filename) => {
    try {
      await documentsAPI.deleteDocument(documentId);
      message.success(`Đã xóa file ${filename}`);
      setNeedsRefresh(true); // Trigger refresh
    } catch (error) {
      message.error('Xóa file thất bại');
      console.error('Delete error:', error);
    }
  };



  const getStatusTag = (status) => {
    const statusConfig = {
      completed: { color: 'success', text: 'Hoàn thành' },
      failed: { color: 'error', text: 'Thất bại' },
      uploading: { color: 'processing', text: 'Đang xử lý' },
      processing: { color: 'processing', text: 'Đang xử lý' },
      pending: { color: 'default', text: 'Chờ xử lý' }
    };

    const config = statusConfig[status] || statusConfig.pending;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  const getFileTypeIcon = (fileType) => {
    switch (fileType) {
      case '.pdf':
        return <FilePdfFilled style={{ color: '#ff4d4f', fontSize: '18px', borderRadius: '4px' }} />;
      case '.docx':
        return <FileWordFilled style={{ color: '#1890ff', fontSize: '18px', borderRadius: '4px' }} />;
      default:
        return <FileTextFilled style={{ color: '#666', fontSize: '18px', borderRadius: '4px' }} />;
    }
  };

  const getFileTypeTag = (fileType) => {
    switch (fileType) {
      case '.pdf':
        return <Tag color="red">PDF</Tag>;
      case '.docx':
        return <Tag color="blue">DOCX</Tag>;
      default:
        return <Tag>Khác</Tag>;
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const columns = [
    {
      title: <span className="font-semibold text-sm">Tên file</span>,
      dataIndex: 'filename',
      key: 'filename',
      render: (text, record) => (
        <div className="icon-text-gap-md">
          {getFileTypeIcon(record.file_type)}
          <span className="font-medium lh-normal" style={{ wordBreak: 'break-word' }}>
            {text}
          </span>
        </div>
      ),
      ellipsis: {
        showTitle: false,
      },
    },
    {
      title: <span className="font-semibold text-sm">Loại</span>,
      dataIndex: 'file_type',
      key: 'file_type',
      render: (fileType) => getFileTypeTag(fileType),
      width: 80,
      responsive: ['sm'],
    },
    {
      title: <span className="font-semibold text-sm">Kích thước</span>,
      dataIndex: 'size',
      key: 'size',
      render: (size) => (
        <span className="text-sm font-medium">{formatFileSize(size)}</span>
      ),
      width: 120,
      responsive: ['md'],
    },
    {
      title: <span className="font-semibold text-sm">Ngày tải lên</span>,
      dataIndex: 'upload_date',
      key: 'upload_date',
      render: (date) => (
        <div className="text-sm">
          <div className="font-medium">{moment(date).format('DD/MM/YYYY')}</div>
          <div className="text-xs" style={{ color: '#6B3410', opacity: 0.8 }}>
            {moment(date).format('HH:mm')}
          </div>
        </div>
      ),
      width: 140,
      responsive: ['lg'],
    },
    {
      title: <span className="font-semibold text-sm">Trạng thái</span>,
      key: 'status',
      render: (_, record) => {
        // Check existing file processing status
        const processingInfo = fileProcessingStatus[record.filename];
        
        if (processingInfo) {
          return (
            <div style={{ minWidth: '100px' }}>
              <div style={{ marginBottom: '4px' }}>
                {getStatusTag(processingInfo.status)}
              </div>
              <Progress 
                percent={processingInfo.progress || 0} 
                size="small"
                strokeColor={{
                  '0%': '#D2691E',
                  '100%': '#CD853F'
                }}
                trailColor="rgba(244, 228, 188, 0.5)"
                status={processingInfo.status === 'failed' ? 'exception' : 'active'}
                showInfo={false}
              />
            </div>
          );
        }
        
        return (
          <Tag color="success" style={{ fontSize: 'clamp(11px, 2vw, 12px)' }}>
            ✅ Hoàn thành
          </Tag>
        );
      },
      width: 120,
      responsive: ['md'],
    },
    {
      title: <span className="font-semibold text-sm">Thao tác</span>,
      key: 'action',
      render: (_, record) => (
        <div className="action-group-secondary" style={{ 
          display: 'flex', 
          gap: 'clamp(4px, 1.5vw, 8px)',
          flexWrap: 'wrap',
          justifyContent: width <= 768 ? 'center' : 'flex-start'
        }}>
          <Button
            icon={<DownloadOutlined />}
            size="small"
            onClick={() => message.info('Tính năng download đang phát triển')}
            aria-label={`Tải xuống file ${record.filename}`}
            className="action-btn-download secondary-action btn-secondary-action hover-scale btn-press interactive-feedback"
            style={{ 
              fontSize: 'clamp(11px, 2.5vw, 12px)',
              height: 'clamp(28px, 6vw, 32px)',
              padding: '0 clamp(6px, 1.5vw, 8px)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <span className="hidden-xs">Tải xuống</span>
          </Button>
          <Popconfirm
            title={<span className="font-medium">Xóa tài liệu</span>}
            description={
              <div className="lh-relaxed">
                Bạn có chắc chắn muốn xóa<br />
                <strong style={{ wordBreak: 'break-word' }}>{record.filename}</strong>?
              </div>
            }
            onConfirm={() => handleDelete(record.id, record.filename)}
            okText="Xóa"
            cancelText="Hủy"
            okType="danger"
          >
            <Button
              icon={<DeleteFilled />}
              size="small"
              danger
              type="text"
              aria-label={`Xóa file ${record.filename}`}
              className="action-btn-delete tertiary-action btn-danger-action"
              style={{ 
                fontSize: 'clamp(11px, 2.5vw, 12px)',
                height: 'clamp(28px, 6vw, 32px)',
                padding: '0 clamp(6px, 1.5vw, 8px)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <span className="hidden-xs">Xóa</span>
            </Button>
          </Popconfirm>
        </div>
      ),
      width: 160,
      fixed: 'right',
    },
  ];



  const totalSize = documents.reduce((sum, doc) => sum + doc.size, 0);
  const pdfCount = documents.filter(doc => doc.file_type === '.pdf').length;
  const docxCount = documents.filter(doc => doc.file_type === '.docx').length;

  return (
    <div style={{ 
      padding: 'clamp(16px, 3vw, 24px)', 
      minHeight: '600px', 
      overflow: 'auto',
      background: 'linear-gradient(135deg, #FDF5E6 0%, #F4E4BC 100%)',
      minHeight: '100vh'
    }}>
      <div className="mb-4">
        <Title 
          level={3} 
          className="mb-1 lh-tight font-semibold" 
          style={{ 
            color: '#D2691E', 
            fontFamily: "'MaisonNeue', 'Inter', sans-serif",
            fontSize: 'clamp(24px, 5vw, 32px)'
          }}
        >
          📁 Quản lý Tài liệu
        </Title>
        <Text 
          type="secondary" 
          className="text-base lh-relaxed"
          style={{
            fontSize: 'clamp(14px, 2.5vw, 16px)',
            color: '#6B3410',
            display: 'block',
            marginBottom: '24px'
          }}
        >
          Xem, quản lý và tải xuống tài liệu đã upload với giao diện trực quan
        </Text>
      </div>

      {/* Statistics */}
      <Row gutter={[width <= 768 ? 12 : 16, width <= 768 ? 12 : 16]} className="mb-4">
        <Col xs={24} sm={12} md={6} lg={6} xl={6}>
          <Card 
            className="text-center stats-card card-animate hover-lift" 
            style={{ 
              height: '100%',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              border: '1px solid #f0f0f0',
              borderRadius: 'clamp(8px, 2vw, 12px)'
            }}
          >
            {loading ? (
              <div style={{ padding: '16px' }}>
                <Skeleton.Avatar active size="small" style={{ marginBottom: '8px' }} />
                <Skeleton active paragraph={{ rows: 1 }} />
              </div>
            ) : (
              <Statistic
                title={<span className="text-sm font-medium" style={{ fontSize: 'clamp(12px, 2.5vw, 14px)' }}>Tổng số tài liệu</span>}
                value={documents.length}
                prefix={<FileTextFilled style={{ fontSize: 'clamp(16px, 3vw, 20px)', padding: '4px', background: 'rgba(210, 105, 30, 0.1)', borderRadius: '6px' }} />}
                valueStyle={{ 
                  color: '#D2691E', 
                  fontSize: 'clamp(24px, 5vw, 32px)',
                  fontWeight: '600',
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                }}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6} lg={6} xl={6}>
          <Card 
            className="text-center stats-card card-animate hover-lift" 
            style={{ 
              height: '100%',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              border: '1px solid #f0f0f0',
              borderRadius: 'clamp(8px, 2vw, 12px)'
            }}
          >
            {loading ? (
              <div style={{ padding: '16px' }}>
                <Skeleton.Avatar active size="small" style={{ marginBottom: '8px' }} />
                <Skeleton active paragraph={{ rows: 1 }} />
              </div>
            ) : (
              <Statistic
                title={<span className="text-sm font-medium" style={{ fontSize: 'clamp(12px, 2.5vw, 14px)' }}>File PDF</span>}
                value={pdfCount}
                prefix={<FilePdfFilled style={{ fontSize: 'clamp(16px, 3vw, 20px)', padding: '4px', background: 'rgba(255, 77, 79, 0.1)', borderRadius: '6px' }} />}
                valueStyle={{ 
                  color: '#ff4d4f', 
                  fontSize: 'clamp(24px, 5vw, 32px)',
                  fontWeight: '600',
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                }}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6} lg={6} xl={6}>
          <Card 
            className="text-center stats-card card-animate hover-lift" 
            style={{ 
              height: '100%',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              border: '1px solid #f0f0f0',
              borderRadius: 'clamp(8px, 2vw, 12px)'
            }}
          >
            {loading ? (
              <div style={{ padding: '16px' }}>
                <Skeleton.Avatar active size="small" style={{ marginBottom: '8px' }} />
                <Skeleton active paragraph={{ rows: 1 }} />
              </div>
            ) : (
              <Statistic
                title={<span className="text-sm font-medium" style={{ fontSize: 'clamp(12px, 2.5vw, 14px)' }}>File DOCX</span>}
                value={docxCount}
                prefix={<FileWordFilled style={{ fontSize: 'clamp(16px, 3vw, 20px)', padding: '4px', background: 'rgba(24, 144, 255, 0.1)', borderRadius: '6px' }} />}
                valueStyle={{ 
                  color: '#1890ff', 
                  fontSize: 'clamp(24px, 5vw, 32px)',
                  fontWeight: '600',
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                }}
              />
            )}
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6} lg={6} xl={6}>
          <Card 
            className="text-center stats-card card-animate hover-lift" 
            style={{ 
              height: '100%',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              border: '1px solid #f0f0f0',
              borderRadius: 'clamp(8px, 2vw, 12px)'
            }}
          >
            {loading ? (
              <div style={{ padding: '16px' }}>
                <Skeleton.Avatar active size="small" style={{ marginBottom: '8px' }} />
                <Skeleton active paragraph={{ rows: 1 }} />
              </div>
            ) : (
              <Statistic
                title={<span className="text-sm font-medium" style={{ fontSize: 'clamp(12px, 2.5vw, 14px)' }}>Tổng dung lượng</span>}
                value={formatFileSize(totalSize)}
                prefix={<DownloadOutlined style={{ fontSize: 'clamp(16px, 3vw, 20px)', padding: '4px', background: 'rgba(82, 196, 26, 0.1)', borderRadius: '6px' }} />}
                valueStyle={{ 
                  color: '#52c41a', 
                  fontSize: 'clamp(20px, 4.5vw, 24px)',
                  fontWeight: '600',
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                }}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Documents Table */}
      <Card 
        className="mb-4"
        title={
          <span style={{ 
            color: '#D2691E', 
            fontWeight: '600',
            fontSize: 'clamp(16px, 3vw, 20px)',
            fontFamily: "'MaisonNeue', 'Inter', sans-serif"
          }}>
            📄 Danh sách tài liệu
          </span>
        }
        style={{
          borderRadius: 'clamp(12px, 2.5vw, 16px)',
          border: '2px solid #F4E4BC',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 8px 32px rgba(210, 105, 30, 0.1)'
        }}
        bodyStyle={{ 
          padding: 'clamp(20px, 4vw, 32px)' 
        }}
      >
        {loading ? (
          <div style={{ padding: '20px' }}>
            <Skeleton active paragraph={{ rows: 6 }} />
            <div style={{ marginTop: '16px' }}>
              <Skeleton.Button active style={{ width: '100px', marginRight: '8px' }} />
              <Skeleton.Button active style={{ width: '80px', marginRight: '8px' }} />
              <Skeleton.Button active style={{ width: '120px' }} />
            </div>
          </div>
        ) : documents.length === 0 ? (
          <Empty
            description={
              <div className="text-center">
                <div className="text-base font-medium mb-1">Chưa có tài liệu nào</div>
                <div className="text-sm" style={{ color: '#6B3410' }}>
                  Tải lên tài liệu đầu tiên để bắt đầu
                </div>
              </div>
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <Table
            columns={columns}
            dataSource={documents}
            rowKey="id"
            pagination={{
              pageSize: width <= 768 ? 5 : 8,
              showSizeChanger: width > 768,
              showQuickJumper: width > 768,
              showTotal: (total, range) => (
                <span className="text-sm font-medium" style={{ fontSize: 'clamp(12px, 2.5vw, 14px)' }}>
                  {width <= 480 ? `${range[0]}-${range[1]}/${total}` : `Hiển thị ${range[0]}-${range[1]} của ${total} tài liệu`}
                </span>
              ),
              pageSizeOptions: ['5', '8', '16', '24'],
              responsive: true,
              size: width <= 768 ? 'small' : 'default'
            }}
            scroll={{ x: width <= 768 ? 600 : 800 }}
            size={width <= 768 ? 'small' : 'middle'}
            rowClassName={(record, index) => 
              index % 2 === 0 ? 'table-row-even' : 'table-row-odd'
            }
            style={{ 
              '--table-row-height': '60px'
            }}
          />
        )}
      </Card>

      {/* Quick Actions */}
      <Card 
        className="mb-4"
        title={
          <span style={{ 
            color: '#D2691E', 
            fontWeight: '600',
            fontSize: 'clamp(16px, 3vw, 20px)',
            fontFamily: "'MaisonNeue', 'Inter', sans-serif"
          }}>
            ⚡ Thao tác nhanh
          </span>
        }
        style={{
          borderRadius: 'clamp(12px, 2.5vw, 16px)',
          border: '2px solid #F4E4BC',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          boxShadow: '0 8px 32px rgba(210, 105, 30, 0.1)'
        }}
        bodyStyle={{ 
          padding: 'clamp(20px, 4vw, 32px)' 
        }}
      >
        <div className="action-group-primary" style={{ 
          display: 'flex', 
          gap: 'clamp(12px, 3vw, 16px)',
          flexWrap: 'wrap',
          justifyContent: width <= 768 ? 'center' : 'flex-start'
        }}>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={() => setNeedsRefresh(true)}
            loading={loading}
            size="large"
            className="refresh-btn primary-action btn-primary-action"
            aria-label="Làm mới danh sách tài liệu"
            style={{ 
              height: 'clamp(40px, 8vw, 48px)',
              fontSize: 'clamp(13px, 2.5vw, 16px)',
              padding: '0 clamp(16px, 4vw, 24px)',
              borderRadius: 'clamp(10px, 2vw, 12px)',
              minWidth: width <= 768 ? '120px' : 'auto'
            }}
          >
            {width <= 480 ? 'Làm mới' : 'Làm mới danh sách'}
          </Button>
        </div>
      </Card>


    </div>
  );
});

export default DocumentManagement;
