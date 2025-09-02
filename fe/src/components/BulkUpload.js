import React, { useState, useCallback, useEffect } from 'react';
import { 
  Upload, 
  Button, 
  Progress, 
  List, 
  Card, 
  Typography, 
  Space, 
  Alert, 
  Tag,
  Divider,
  notification
} from 'antd';
import { 
  InboxOutlined, 
  UploadOutlined, 
  DeleteOutlined, 
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import websocketService from '../services/websocket';

const { Dragger } = Upload;
const { Title, Text } = Typography;

const BulkUpload = () => {
  const { user } = useAuth();
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [bulkProgress, setBulkProgress] = useState(null);
  const [uploadResults, setUploadResults] = useState(null);

  // WebSocket event handlers
  useEffect(() => {
    if (!user?.username) return;

    // Connect WebSocket if not connected
    if (!websocketService.isSocketConnected()) {
      websocketService.connect(user.username);
    }

    const handleBulkProgress = (data) => {
      setBulkProgress(data);
    };

    const handleBulkComplete = (data) => {
      setUploading(false);
      setBulkProgress(null);
      setUploadResults(data);
      
      notification.success({
        message: 'Bulk Upload Complete',
        description: `Successfully uploaded ${data.successful_uploads?.length || 0} files`,
        duration: 5
      });
    };

    const handleBulkError = (data) => {
      setUploading(false);
      setBulkProgress(null);
      
      notification.error({
        message: 'Bulk Upload Failed',
        description: data.error || 'An error occurred during bulk upload',
        duration: 5
      });
    };

    const handleFileProgress = (data) => {
      setUploadProgress(prev => ({
        ...prev,
        [data.task_id]: data
      }));
    };

    const handleFileComplete = (data) => {
      setUploadProgress(prev => ({
        ...prev,
        [data.task_id]: { ...data, status: 'completed' }
      }));
    };

    const handleFileError = (data) => {
      setUploadProgress(prev => ({
        ...prev,
        [data.task_id]: { ...data, status: 'failed' }
      }));
    };

    // Register event listeners
    websocketService.on('bulk_upload_progress', handleBulkProgress);
    websocketService.on('bulk_upload_complete', handleBulkComplete);
    websocketService.on('bulk_upload_error', handleBulkError);
    websocketService.on('file_upload_progress', handleFileProgress);
    websocketService.on('file_upload_complete', handleFileComplete);
    websocketService.on('file_upload_error', handleFileError);

    return () => {
      // Cleanup event listeners
      websocketService.off('bulk_upload_progress', handleBulkProgress);
      websocketService.off('bulk_upload_complete', handleBulkComplete);
      websocketService.off('bulk_upload_error', handleBulkError);
      websocketService.off('file_upload_progress', handleFileProgress);
      websocketService.off('file_upload_complete', handleFileComplete);
      websocketService.off('file_upload_error', handleFileError);
    };
  }, [user?.username]);

  const uploadProps = {
    name: 'file',
    multiple: true,
    fileList,
    beforeUpload: () => false, // Prevent automatic upload
    onChange: (info) => {
      setFileList(info.fileList);
    },
    onDrop: (e) => {
      console.log('Dropped files', e.dataTransfer.files);
    },
    accept: '.pdf,.docx,.doc,.txt,.png,.jpg,.jpeg',
    maxCount: 50,
  };

  const handleBulkUpload = async () => {
    if (fileList.length === 0) {
      notification.warning({
        message: 'No Files Selected',
        description: 'Please select files to upload',
      });
      return;
    }

    setUploading(true);
    setUploadResults(null);
    setBulkProgress(null);
    setUploadProgress({});

    try {
      const formData = new FormData();
      fileList.forEach((file) => {
        formData.append('files', file.originFileObj);
      });

      const response = await api.post('/api/documents/bulk-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      notification.success({
        message: 'Upload Started',
        description: response.data.message,
      });

    } catch (error) {
      setUploading(false);
      console.error('Upload error:', error);
      
      notification.error({
        message: 'Upload Failed',
        description: error.response?.data?.detail || 'Failed to start upload',
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
  };

  const getFileIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: '#f5222d' }} />;
      case 'uploading':
        return <SyncOutlined spin style={{ color: '#1890ff' }} />;
      default:
        return null;
    }
  };

  const getStatusTag = (status) => {
    const statusConfig = {
      completed: { color: 'success', text: 'Completed' },
      failed: { color: 'error', text: 'Failed' },
      uploading: { color: 'processing', text: 'Uploading' },
      pending: { color: 'default', text: 'Pending' }
    };

    const config = statusConfig[status] || statusConfig.pending;
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={3}>Bulk File Upload</Title>
        <Text type="secondary">
          Upload multiple files at once. Supported formats: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG
        </Text>

        <Divider />

        <Dragger {...uploadProps} style={{ marginBottom: '24px' }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Click or drag files to this area to upload</p>
          <p className="ant-upload-hint">
            Support for multiple file selection. Maximum 50 files per batch.
          </p>
        </Dragger>

        {fileList.length > 0 && (
          <Card size="small" style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <Text strong>Selected Files ({fileList.length})</Text>
              <Space>
                <Button 
                  type="primary" 
                  icon={<UploadOutlined />}
                  onClick={handleBulkUpload}
                  loading={uploading}
                  disabled={fileList.length === 0}
                >
                  Upload All Files
                </Button>
                <Button 
                  icon={<DeleteOutlined />}
                  onClick={handleClearAll}
                  disabled={uploading}
                >
                  Clear All
                </Button>
              </Space>
            </div>

            <List
              size="small"
              dataSource={fileList}
              renderItem={(file) => {
                const progressData = Object.values(uploadProgress).find(p => 
                  p.filename === file.name
                );
                
                return (
                  <List.Item
                    actions={[
                      getFileIcon(progressData?.status),
                      !uploading && (
                        <Button 
                          type="text" 
                          size="small"
                          icon={<DeleteOutlined />}
                          onClick={() => handleRemoveFile(file)}
                        />
                      )
                    ].filter(Boolean)}
                  >
                    <List.Item.Meta
                      title={
                        <Space>
                          <Text>{file.name}</Text>
                          {progressData && getStatusTag(progressData.status)}
                        </Space>
                      }
                      description={
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <Text type="secondary">
                            Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                          </Text>
                          {progressData?.progress && (
                            <Progress 
                              percent={progressData.progress} 
                              size="small"
                              status={progressData.status === 'failed' ? 'exception' : 'active'}
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
          <Alert
            message={`Processing Files (${bulkProgress.completed_files}/${bulkProgress.total_files})`}
            description={
              <Progress 
                percent={bulkProgress.progress} 
                status="active"
                format={percent => `${percent}% (${bulkProgress.completed_files}/${bulkProgress.total_files})`}
              />
            }
            type="info"
            style={{ marginBottom: '16px' }}
          />
        )}

        {uploadResults && (
          <Card title="Upload Results" style={{ marginTop: '16px' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Total Files: </Text>
                <Text>{uploadResults.total_files}</Text>
              </div>
              <div>
                <Text strong>Successful: </Text>
                <Text style={{ color: '#52c41a' }}>{uploadResults.successful_uploads?.length || 0}</Text>
              </div>
              <div>
                <Text strong>Failed: </Text>
                <Text style={{ color: '#f5222d' }}>{uploadResults.failed_files?.length || 0}</Text>
              </div>

              {uploadResults.successful_uploads?.length > 0 && (
                <div>
                  <Title level={5}>Successfully Uploaded Files:</Title>
                  <List
                    size="small"
                    dataSource={uploadResults.successful_uploads}
                    renderItem={(item) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                          title={item.filename}
                          description={
                            <a href={item.public_url} target="_blank" rel="noopener noreferrer">
                              View File
                            </a>
                          }
                        />
                      </List.Item>
                    )}
                  />
                </div>
              )}

              {uploadResults.failed_files?.length > 0 && (
                <div>
                  <Title level={5}>Failed Files:</Title>
                  <List
                    size="small"
                    dataSource={uploadResults.failed_files}
                    renderItem={(item) => (
                      <List.Item>
                        <List.Item.Meta
                          avatar={<ExclamationCircleOutlined style={{ color: '#f5222d' }} />}
                          title={item.filename}
                          description={<Text type="danger">{item.error}</Text>}
                        />
                      </List.Item>
                    )}
                  />
                </div>
              )}
            </Space>
          </Card>
        )}
      </Card>
    </div>
  );
};

export default BulkUpload;
