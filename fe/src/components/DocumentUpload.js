import React, { useState, useEffect } from 'react';
import {
  Upload,
  Button,
  Typography,
  message,
  Card,
  Row,
  Col,
  Statistic,
  Spin,
  Progress,
  notification,
  List,
  Alert,
  Space,
  Tag
} from 'antd';
import {
  UploadOutlined,
  DeleteFilled,
  InboxOutlined,
  SyncOutlined,
  CheckCircleFilled,
  ExclamationCircleFilled,
  CloudUploadOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { documentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import websocketService from '../services/websocket';

const { Title, Text } = Typography;
const { Dragger } = Upload;

const DocumentUpload = React.memo(() => {
  const { user } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  
  // Bulk upload states
  const [fileList, setFileList] = useState([]);
  const [bulkProgress, setBulkProgress] = useState(null);
  const [uploadResults, setUploadResults] = useState(null);
  
  // Individual file upload tracking
  const [documentUploadProgress, setDocumentUploadProgress] = useState({});
  
  // Track active uploads
  const [activeUploads, setActiveUploads] = useState(new Set());

  useEffect(() => {
    // Connect WebSocket if user is available
    if (user?.username && !websocketService.isSocketConnected()) {
      websocketService.connect(user.username);
    }
    
    // Setup WebSocket event listeners
    const handleFileProgress = (data) => {
      setUploadProgress(prev => ({
        ...prev,
        [data.task_id]: data
      }));
      
      // Track active upload
      setActiveUploads(prev => new Set(prev).add(data.task_id));
      
      // Track progress by filename for new uploads
      setDocumentUploadProgress(prev => ({
        ...prev,
        [data.filename]: {
          progress: data.progress,
          status: data.status,
          task_id: data.task_id
        }
      }));
    };
    
    const handleFileComplete = (data) => {
      setUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[data.task_id];
        return newProgress;
      });
      
      // Remove from active uploads
      setActiveUploads(prev => {
        const newSet = new Set(prev);
        newSet.delete(data.task_id);
        return newSet;
      });
      
      // Clear document upload progress
      setDocumentUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[data.filename];
        return newProgress;
      });
      
      notification.success({
        message: 'Upload Complete',
        description: `File ${data.filename} uploaded successfully`,
        duration: 3
      });
    };
    
    const handleFileError = (data) => {
      setUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[data.task_id];
        return newProgress;
      });
      
      // Remove from active uploads
      setActiveUploads(prev => {
        const newSet = new Set(prev);
        newSet.delete(data.task_id);
        return newSet;
      });
      
      // Clear document upload progress
      setDocumentUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[data.filename];
        return newProgress;
      });
      
      notification.error({
        message: 'Upload Failed',
        description: `File ${data.filename} upload failed: ${data.error}`,
        duration: 5
      });
    };

    // Bulk upload handlers
    const handleBulkProgress = (data) => {
      setBulkProgress(data);
    };

    const handleBulkComplete = (data) => {
      setBulkProgress(null);
      setUploadResults(data);
      
      notification.success({
        message: 'Upload đồng loạt hoàn thành',
        description: `Đã tải lên thành công ${data.successful_uploads?.length || 0} file`,
        duration: 5
      });
    };

    const handleBulkError = (data) => {
      setBulkProgress(null);
      
      notification.error({
        message: 'Upload đồng loạt thất bại',
        description: data.error || 'Có lỗi xảy ra trong quá trình upload',
        duration: 5
      });
    };

    websocketService.on('file_upload_progress', handleFileProgress);
    websocketService.on('file_upload_complete', handleFileComplete);
    websocketService.on('file_upload_error', handleFileError);
    websocketService.on('file_processing_update', handleFileProgress); // Also handle processing updates
    websocketService.on('bulk_upload_progress', handleBulkProgress);
    websocketService.on('bulk_upload_complete', handleBulkComplete);
    websocketService.on('bulk_upload_error', handleBulkError);
    
    return () => {
      websocketService.off('file_upload_progress', handleFileProgress);
      websocketService.off('file_upload_complete', handleFileComplete);
      websocketService.off('file_upload_error', handleFileError);
      websocketService.off('file_processing_update', handleFileProgress);
      websocketService.off('bulk_upload_progress', handleBulkProgress);
      websocketService.off('bulk_upload_complete', handleBulkComplete);
      websocketService.off('bulk_upload_error', handleBulkError);
    };
  }, [user?.username]);

  // Update uploading state based on active uploads
  useEffect(() => {
    setUploading(activeUploads.size > 0 || bulkProgress !== null);
  }, [activeUploads.size, bulkProgress]);

  const handleUpload = async (file) => {
    // Kiểm tra loại file
    const allowedTypes = ['.pdf', '.docx', '.doc', '.txt', '.md', '.png', '.jpg', '.jpeg'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      message.error('Chỉ hỗ trợ file PDF, DOCX, DOC, TXT, MD (Markdown), PNG, JPG, JPEG!');
      return false;
    }

    // Kiểm tra kích thước file (100MB - configurable)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
      message.error('Kích thước file không được vượt quá 100MB!');
      return false;
    }

    // Mark file as uploading in document progress
    setDocumentUploadProgress(prev => ({
      ...prev,
      [file.name]: {
        progress: 0,
        status: 'uploading',
        task_id: null
      }
    }));
    
    try {
      const response = await documentsAPI.uploadDocument(file);
      
      // Add to active uploads tracking using task_id from response
      if (response.data?.task_id) {
        setActiveUploads(prev => new Set(prev).add(response.data.task_id));
      }
      
      message.success({
        content: `File ${file.name} đã được gửi để xử lý. Bạn sẽ nhận được thông báo khi hoàn thành.`,
        duration: 3
      });
      
      console.log('Upload task started:', response.data);
    } catch (error) {
      // Clear progress on error
      setDocumentUploadProgress(prev => {
        const newProgress = { ...prev };
        delete newProgress[file.name];
        return newProgress;
      });
      
      message.error(`Tải lên thất bại: ${error.response?.data?.detail || 'Lỗi không xác định'}`);
      console.error('Upload error:', error);
    }

    return false; // Prevent default upload behavior
  };

  // Bulk upload functions
  const handleBulkUpload = async () => {
    if (fileList.length === 0) {
      notification.warning({
        message: 'Chưa chọn file',
        description: 'Vui lòng chọn file để tải lên',
      });
      return;
    }

    setUploadResults(null);
    setBulkProgress(null);
    setUploadProgress({});

    try {
      const formData = new FormData();
      fileList.forEach((file) => {
        formData.append('files', file.originFileObj);
      });

      const response = await documentsAPI.bulkUploadDocuments(formData);

      notification.success({
        message: 'Bắt đầu upload',
        description: response.message,
      });

    } catch (error) {
      console.error('Upload error:', error);
      
      notification.error({
        message: 'Upload thất bại',
        description: error.response?.data?.detail || 'Không thể bắt đầu upload',
      });
    }
  };

  const handleRemoveFile = (file) => {
    const newFileList = fileList.filter(item => item.uid !== file.uid);
    setFileList(newFileList);
  };

  const handleClearAll = () => {
    setFileList([]);
    setUploadProgress({});
    setUploadResults(null);
    setBulkProgress(null);
    setDocumentUploadProgress({});
    setActiveUploads(new Set());
  };

  const getFileIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleFilled style={{ color: '#52c41a', padding: '2px', background: 'rgba(82, 196, 26, 0.1)', borderRadius: '50%' }} />;
      case 'failed':
        return <ExclamationCircleFilled style={{ color: '#f5222d', padding: '2px', background: 'rgba(245, 34, 45, 0.1)', borderRadius: '50%' }} />;
      case 'uploading':
        return <SyncOutlined spin style={{ color: '#1890ff', padding: '2px', background: 'rgba(24, 144, 255, 0.1)', borderRadius: '50%' }} />;
      default:
        return null;
    }
  };

  const getStatusTag = (status) => {
    const statusConfig = {
      completed: { color: 'success', text: '✅ Hoàn thành' },
      failed: { color: 'error', text: '❌ Thất bại' },
      uploading: { color: 'processing', text: '⬆️ Đang tải lên' },
      extracting_content: { color: 'processing', text: '🔍 Trích xuất nội dung' },
      uploading_to_cloud: { color: 'processing', text: '☁️ Lưu cloud storage' },
      saving_to_vector_db: { color: 'processing', text: '🗄️ Lưu vector DB' },
      finalizing: { color: 'processing', text: '🔄 Đang hoàn tất' },
      processing: { color: 'processing', text: '⚙️ Đang xử lý' },
      pending: { color: 'default', text: '⏳ Chờ xử lý' }
    };

    const config = statusConfig[status] || statusConfig.pending;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // Combined upload props for both single and multiple files
  const combinedUploadProps = {
    name: 'file',
    multiple: true,
    fileList,
    beforeUpload: () => false, // Prevent automatic upload
    onChange: (info) => {
      setFileList(info.fileList);
      
      // If only one file is selected, auto-trigger single upload
      if (info.fileList.length === 1 && !uploading) {
        const file = info.fileList[0].originFileObj;
        // Auto upload single file
        handleUpload(file);
        // Clear the file list after single upload
        setTimeout(() => setFileList([]), 100);
      }
    },
    accept: '.pdf,.docx,.doc,.txt,.md,.png,.jpg,.jpeg',
    maxCount: 50,
  };

  const uploadProps = {
    multiple: true,
    beforeUpload: handleUpload,
    showUploadList: false,
    accept: '.pdf,.docx,.doc,.txt,.md,.png,.jpg,.jpeg',
  };

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
          📤 Tải lên Tài liệu
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
          Tải lên tài liệu đơn lẻ hoặc hàng loạt với giao diện thân thiện và theo dõi tiến trình realtime
        </Text>
      </div>

      {/* Upload Instructions */}
      <Alert
        message="Hướng dẫn sử dụng"
        description={
          <div style={{ lineHeight: '1.6', fontSize: 'clamp(13px, 2.5vw, 14px)' }}>
            <p style={{ margin: '8px 0' }}>
              🎯 <strong>Upload đơn lẻ:</strong> Chọn 1 file hoặc kéo thả → Upload ngay lập tức
            </p>
            <p style={{ margin: '8px 0' }}>
              📂 <strong>Upload hàng loạt:</strong> Chọn nhiều file → Kiểm tra danh sách → Nhấn "Tải lên tất cả"
            </p>
            <p style={{ margin: '8px 0' }}>
              ✅ <strong>Định dạng:</strong> PDF, DOCX, DOC, TXT, MD (Markdown), PNG, JPG, JPEG • Tối đa 100MB/file • 50 file/lần
            </p>
            <p style={{ margin: '8px 0' }}>
              🤖 <strong>AI Tự động:</strong> Trích xuất văn bản từ PDF, Markdown & hình ảnh • Header preservation cho chunks • Lưu vào vector database để tìm kiếm thông minh
            </p>
          </div>
        }
        type="info"
        showIcon
        style={{ 
          marginBottom: '24px',
          borderRadius: '12px',
          border: '2px solid #91caff',
          background: 'rgba(240, 249, 255, 0.8)'
        }}
      />

      {/* Upload Area */}
      <Card 
        className="upload-card mb-4"
        title={
          <span style={{ 
            color: '#D2691E', 
            fontWeight: '600',
            fontSize: 'clamp(16px, 3vw, 20px)',
            fontFamily: "'MaisonNeue', 'Inter', sans-serif"
          }}>
            🎯 Khu vực Tải lên
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
        {/* Combined Upload Area */}
        <div style={{ padding: 'clamp(16px, 3vw, 24px) 0' }}>
          <Dragger 
            {...combinedUploadProps} 
            style={{ 
              marginBottom: '24px',
              borderRadius: '16px',
              border: '2px dashed #D2691E',
              background: 'linear-gradient(135deg, #FDF5E6 0%, rgba(222, 184, 135, 0.3) 100%)'
            }}
            className="earth-dragger"
          >
            <div style={{ padding: 'clamp(24px, 5vw, 48px) clamp(16px, 3vw, 24px)' }}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined 
                  style={{ 
                    color: '#D2691E', 
                    fontSize: 'clamp(48px, 8vw, 64px)',
                    marginBottom: '16px'
                  }} 
                />
              </p>
              <p 
                className="ant-upload-text" 
                style={{ 
                  color: '#D2691E', 
                  fontSize: 'clamp(16px, 3vw, 20px)',
                  fontWeight: '600',
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif",
                  margin: '16px 0 8px 0'
                }}
              >
                Kéo thả file vào đây để upload
              </p>
              <p 
                className="ant-upload-hint" 
                style={{ 
                  fontSize: 'clamp(13px, 2.5vw, 15px)',
                  color: '#A0522D',
                  margin: '8px 0 0 0',
                  lineHeight: '1.6'
                }}
              >
                ✨ 1 file = Upload ngay • Nhiều file = Hiển thị danh sách để xử lý hàng loạt • Tối đa 50 file • 100MB/file
              </p>
            </div>
          </Dragger>
          
          <div style={{ 
            display: 'flex', 
            gap: 'clamp(12px, 3vw, 16px)',
            flexWrap: 'wrap',
            justifyContent: window.innerWidth <= 768 ? 'center' : 'flex-start',
            marginBottom: '24px'
          }}>
            <Upload {...uploadProps}>
              <Button 
                icon={<UploadOutlined />} 
                loading={uploading}
                className="btn-government upload-btn"
                size="large"
                style={{ 
                  height: 'clamp(40px, 8vw, 48px)',
                  fontWeight: '500',
                  letterSpacing: '0.01em',
                  fontSize: 'clamp(13px, 2.5vw, 16px)',
                  padding: '0 clamp(16px, 4vw, 24px)',
                  borderRadius: 'clamp(12px, 2vw, 16px)',
                  minWidth: window.innerWidth <= 768 ? '140px' : 'auto',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
              >
                {uploading ? 'Đang tải lên...' : (window.innerWidth <= 480 ? 'Chọn file' : 'Chọn file từ máy')}
              </Button>
            </Upload>
          </div>

          {fileList.length > 0 && (
            <Card 
              className="file-list-card"
              style={{ 
                marginBottom: 'clamp(16px, 3vw, 24px)',
                borderRadius: '12px',
                border: '1px solid #F4E4BC',
                background: 'rgba(255, 255, 255, 0.8)'
              }}
              bodyStyle={{ 
                padding: 'clamp(16px, 3vw, 24px)' 
              }}
              title={
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: window.innerWidth <= 768 ? 'flex-start' : 'center',
                  flexDirection: window.innerWidth <= 768 ? 'column' : 'row',
                  gap: window.innerWidth <= 768 ? '16px' : '8px'
                }}>
                  <div>
                    <Text 
                      strong 
                      style={{
                        fontSize: 'clamp(16px, 3vw, 18px)',
                        color: '#D2691E',
                        fontFamily: "'MaisonNeue', 'Inter', sans-serif",
                        fontWeight: '600'
                      }}
                    >
                      📂 File đã chọn ({fileList.length})
                    </Text>
                    <div style={{ 
                      fontSize: 'clamp(12px, 2.5vw, 14px)',
                      color: '#6B3410',
                      marginTop: '4px' 
                    }}>
                      Tổng dung lượng: {(fileList.reduce((sum, file) => sum + file.size, 0) / 1024 / 1024).toFixed(2)} MB
                    </div>
                  </div>
                  <Space 
                    direction={window.innerWidth <= 480 ? 'vertical' : 'horizontal'}
                    style={{ 
                      width: window.innerWidth <= 768 ? '100%' : 'auto' 
                    }}
                  >
                    <Button 
                      type="primary" 
                      icon={<CloudUploadOutlined />}
                      onClick={handleBulkUpload}
                      loading={uploading}
                      disabled={fileList.length === 0}
                      className="btn-government upload-btn primary-action btn-primary-action"
                      size="large"
                      style={{
                        height: 'clamp(40px, 8vw, 48px)',
                        fontSize: 'clamp(14px, 2.5vw, 16px)',
                        borderRadius: 'clamp(12px, 2vw, 16px)',
                        width: window.innerWidth <= 768 ? '100%' : 'auto',
                        minWidth: window.innerWidth <= 768 ? '120px' : '160px'
                      }}
                    >
                      {uploading ? '🔄 Đang tải lên...' : '⬆️ Tải lên tất cả'}
                    </Button>
                    <Button 
                      icon={<DeleteFilled />}
                      onClick={handleClearAll}
                      disabled={uploading}
                      size="large"
                      className="clear-btn secondary-action btn-secondary-action"
                      style={{
                        height: 'clamp(40px, 8vw, 48px)',
                        fontSize: 'clamp(14px, 2.5vw, 16px)',
                        borderRadius: 'clamp(10px, 2vw, 12px)',
                        width: window.innerWidth <= 768 ? '100%' : 'auto',
                        minWidth: window.innerWidth <= 768 ? '120px' : '140px'
                      }}
                    >
                      🗑️ Xóa tất cả
                    </Button>
                  </Space>
                </div>
              }
            >
              <List
                size="small"
                dataSource={fileList}
                style={{ 
                  background: 'rgba(253, 245, 230, 0.5)',
                  borderRadius: '8px',
                  padding: '8px'
                }}
                renderItem={(file) => {
                  const progressData = Object.values(uploadProgress).find(p => 
                    p.filename === file.name
                  );
                  
                  return (
                    <List.Item
                      style={{
                        padding: 'clamp(12px, 2.5vw, 16px)',
                        borderRadius: '8px',
                        background: 'rgba(255, 255, 255, 0.7)',
                        marginBottom: '8px',
                        border: '1px solid rgba(244, 228, 188, 0.6)',
                        transition: 'all 0.3s ease'
                      }}
                      actions={[
                        getFileIcon(progressData?.status),
                        !uploading && (
                                                  <Button 
                          type="text" 
                          size="small"
                          icon={<DeleteFilled />}
                          onClick={() => handleRemoveFile(file)}
                          aria-label={`Xóa file ${file.name} khỏi danh sách`}
                          style={{
                            color: '#A0522D',
                            borderRadius: '8px',
                            height: 'clamp(28px, 6vw, 32px)',
                            width: 'clamp(28px, 6vw, 32px)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                          className="file-remove-btn"
                        />
                        )
                      ].filter(Boolean)}
                    >
                      <List.Item.Meta
                        title={
                          <Space direction="vertical" size={4} style={{ width: '100%' }}>
                            <div style={{ 
                              display: 'flex', 
                              alignItems: 'center', 
                              gap: '8px',
                              flexWrap: 'wrap'
                            }}>
                              <Text 
                                style={{
                                  fontSize: 'clamp(14px, 2.5vw, 16px)',
                                  fontWeight: '500',
                                  color: '#D2691E',
                                  wordBreak: 'break-word',
                                  flex: '1',
                                  minWidth: '0'
                                }}
                              >
                                📄 {file.name}
                              </Text>
                              {progressData && getStatusTag(progressData.status)}
                            </div>
                            <div style={{ 
                              display: 'flex', 
                              gap: 'clamp(12px, 3vw, 20px)',
                              fontSize: 'clamp(12px, 2vw, 13px)',
                              color: '#6B3410'
                            }}>
                              <span>📏 {(file.size / 1024 / 1024).toFixed(2)} MB</span>
                              <span>📅 {file.type || 'Unknown'}</span>
                            </div>
                            {progressData?.progress !== undefined && (
                              <Progress 
                                percent={progressData.progress} 
                                size="small"
                                strokeColor={{
                                  '0%': '#D2691E',
                                  '100%': '#CD853F'
                                }}
                                trailColor="rgba(244, 228, 188, 0.5)"
                                status={progressData.status === 'failed' ? 'exception' : 'active'}
                                style={{ marginTop: '8px' }}
                              />
                            )}
                          </Space>
                        }
                      />
                    </List.Item>
                  );
                }}
              />
            </Card>
          )}

          {bulkProgress && (
            <Card
              title={
                <span style={{ 
                  color: '#D2691E', 
                  fontWeight: '600',
                  fontSize: 'clamp(16px, 3vw, 18px)',
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                }}>
                  <SyncOutlined spin style={{ marginRight: '8px' }} />
                  🔄 Đang xử lý file ({bulkProgress.completed_files}/{bulkProgress.total_files})
                </span>
              }
              style={{ 
                marginBottom: 'clamp(16px, 3vw, 24px)',
                borderRadius: '12px',
                border: '2px solid #DEB887',
                background: 'rgba(222, 184, 135, 0.1)'
              }}
              bodyStyle={{ 
                padding: 'clamp(16px, 3vw, 24px)' 
              }}
            >
              <div style={{ marginBottom: '16px' }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '8px'
                }}>
                  <Text style={{ 
                    fontSize: 'clamp(14px, 2.5vw, 16px)',
                    color: '#6B3410',
                    fontWeight: '500'
                  }}>
                    Tiến trình xử lý:
                  </Text>
                  <Text style={{ 
                    fontSize: 'clamp(14px, 2.5vw, 16px)',
                    color: '#D2691E',
                    fontWeight: '600'
                  }}>
                    {Math.round(bulkProgress.progress)}%
                  </Text>
                </div>
                <Progress 
                  percent={bulkProgress.progress} 
                  status="active"
                  strokeColor={{
                    '0%': '#D2691E',
                    '100%': '#CD853F'
                  }}
                  trailColor="rgba(244, 228, 188, 0.5)"
                  size="default"
                  format={percent => `${Math.round(percent)}%`}
                  style={{ marginBottom: '8px' }}
                />
                <div style={{ 
                  fontSize: 'clamp(12px, 2vw, 14px)',
                  color: '#A0522D',
                  textAlign: 'center'
                }}>
                  Đã hoàn thành: {bulkProgress.completed_files} / {bulkProgress.total_files} file
                </div>
              </div>
            </Card>
          )}

          {uploadResults && (
            <Card 
              title={
                <span style={{ 
                  color: '#D2691E', 
                  fontWeight: '600',
                  fontSize: 'clamp(16px, 3vw, 18px)',
                  fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                }}>
                  📊 Kết quả Upload
                </span>
              }
              style={{ 
                marginTop: 'clamp(16px, 3vw, 24px)',
                borderRadius: '12px',
                border: '2px solid #F4E4BC',
                background: 'rgba(255, 255, 255, 0.95)'
              }}
              bodyStyle={{ 
                padding: 'clamp(16px, 3vw, 24px)' 
              }}
            >
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                {/* Summary Stats */}
                <div style={{ 
                  display: 'flex', 
                  gap: 'clamp(16px, 4vw, 32px)',
                  flexWrap: 'wrap',
                  justifyContent: 'center'
                }}>
                  <div style={{ 
                    textAlign: 'center',
                    padding: 'clamp(12px, 3vw, 16px)',
                    borderRadius: '8px',
                    background: 'rgba(253, 245, 230, 0.8)',
                    border: '1px solid #F4E4BC',
                    minWidth: '100px'
                  }}>
                    <div style={{ 
                      fontSize: 'clamp(20px, 4vw, 28px)',
                      fontWeight: '700',
                      color: '#D2691E',
                      fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                    }}>
                      {uploadResults.total_files}
                    </div>
                    <div style={{ 
                      fontSize: 'clamp(12px, 2vw, 14px)',
                      color: '#6B3410'
                    }}>
                      📁 Tổng file
                    </div>
                  </div>
                  
                  <div style={{ 
                    textAlign: 'center',
                    padding: 'clamp(12px, 3vw, 16px)',
                    borderRadius: '8px',
                    background: 'rgba(82, 196, 26, 0.1)',
                    border: '1px solid rgba(82, 196, 26, 0.3)',
                    minWidth: '100px'
                  }}>
                    <div style={{ 
                      fontSize: 'clamp(20px, 4vw, 28px)',
                      fontWeight: '700',
                      color: '#52c41a',
                      fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                    }}>
                      {uploadResults.successful_uploads?.length || 0}
                    </div>
                    <div style={{ 
                      fontSize: 'clamp(12px, 2vw, 14px)',
                      color: '#52c41a'
                    }}>
                      ✅ Thành công
                    </div>
                  </div>
                  
                  <div style={{ 
                    textAlign: 'center',
                    padding: 'clamp(12px, 3vw, 16px)',
                    borderRadius: '8px',
                    background: 'rgba(245, 34, 45, 0.1)',
                    border: '1px solid rgba(245, 34, 45, 0.3)',
                    minWidth: '100px'
                  }}>
                    <div style={{ 
                      fontSize: 'clamp(20px, 4vw, 28px)',
                      fontWeight: '700',
                      color: '#f5222d',
                      fontFamily: "'MaisonNeue', 'Inter', sans-serif"
                    }}>
                      {uploadResults.failed_files?.length || 0}
                    </div>
                    <div style={{ 
                      fontSize: 'clamp(12px, 2vw, 14px)',
                      color: '#f5222d'
                    }}>
                      ❌ Thất bại
                    </div>
                  </div>
                </div>

                {/* Success Files */}
                {uploadResults.successful_uploads?.length > 0 && (
                  <div>
                    <Title 
                      level={5} 
                      style={{ 
                        color: '#52c41a',
                        fontSize: 'clamp(14px, 2.5vw, 16px)',
                        marginBottom: '12px'
                      }}
                    >
                      ✅ File đã tải lên thành công:
                    </Title>
                    <List
                      size="small"
                      style={{ 
                        background: 'rgba(82, 196, 26, 0.05)',
                        borderRadius: '8px',
                        padding: '8px'
                      }}
                      dataSource={uploadResults.successful_uploads}
                      renderItem={(item) => (
                        <List.Item
                          style={{
                            padding: 'clamp(8px, 2vw, 12px)',
                            background: 'rgba(255, 255, 255, 0.8)',
                            borderRadius: '6px',
                            marginBottom: '4px',
                            border: '1px solid rgba(82, 196, 26, 0.2)'
                          }}
                        >
                          <List.Item.Meta
                            avatar={<CheckCircleFilled style={{ color: '#52c41a', fontSize: '16px', padding: '4px', background: 'rgba(82, 196, 26, 0.1)', borderRadius: '50%' }} />}
                            title={
                              <Text style={{ 
                                fontSize: 'clamp(13px, 2.5vw, 15px)',
                                color: '#D2691E',
                                fontWeight: '500'
                              }}>
                                📄 {item.filename}
                              </Text>
                            }
                            description={
                              item.public_url && (
                                <a 
                                  href={item.public_url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  style={{ 
                                    fontSize: 'clamp(12px, 2vw, 13px)',
                                    color: '#1890ff'
                                  }}
                                >
                                  🔗 Xem file
                                </a>
                              )
                            }
                          />
                        </List.Item>
                      )}
                    />
                  </div>
                )}

                {/* Failed Files */}
                {uploadResults.failed_files?.length > 0 && (
                  <div>
                    <Title 
                      level={5} 
                      style={{ 
                        color: '#f5222d',
                        fontSize: 'clamp(14px, 2.5vw, 16px)',
                        marginBottom: '12px'
                      }}
                    >
                      ❌ File tải lên thất bại:
                    </Title>
                    <List
                      size="small"
                      style={{ 
                        background: 'rgba(245, 34, 45, 0.05)',
                        borderRadius: '8px',
                        padding: '8px'
                      }}
                      dataSource={uploadResults.failed_files}
                      renderItem={(item) => (
                        <List.Item
                          style={{
                            padding: 'clamp(8px, 2vw, 12px)',
                            background: 'rgba(255, 255, 255, 0.8)',
                            borderRadius: '6px',
                            marginBottom: '4px',
                            border: '1px solid rgba(245, 34, 45, 0.2)'
                          }}
                        >
                          <List.Item.Meta
                            avatar={<ExclamationCircleFilled style={{ color: '#f5222d', fontSize: '16px', padding: '4px', background: 'rgba(245, 34, 45, 0.1)', borderRadius: '50%' }} />}
                            title={
                              <Text style={{ 
                                fontSize: 'clamp(13px, 2.5vw, 15px)',
                                color: '#D2691E',
                                fontWeight: '500'
                              }}>
                                📄 {item.filename}
                              </Text>
                            }
                            description={
                              <Text 
                                type="danger" 
                                style={{ 
                                  fontSize: 'clamp(12px, 2vw, 13px)'
                                }}
                              >
                                ⚠️ {item.error}
                              </Text>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  </div>
                )}
              </Space>
            </Card>
          )}
        </div>
      </Card>

      {/* Upload Progress */}
      {Object.keys(uploadProgress).length > 0 && (
        <Card 
          title={
            <span className="text-lg font-semibold" style={{ color: '#D2691E' }}>
              <SyncOutlined spin /> Upload Progress
            </span>
          }
          className="mb-4"
          bodyStyle={{ padding: '24px' }}
        >
          {Object.entries(uploadProgress).map(([taskId, progress]) => (
            <div key={taskId} style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="font-medium" style={{ color: '#D2691E' }}>{progress.filename}</span>
                {getStatusTag(progress.status)}
              </div>
              <Progress 
                percent={progress.progress || 0} 
                status={progress.status === 'failed' ? 'exception' : 'active'}
                showInfo={true}
                format={percent => `${percent}%`}
              />
            </div>
          ))}
        </Card>
      )}
    </div>
  );
});

export default DocumentUpload;
