import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Typography,
  Spin,
  Alert,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Modal,
  Statistic,
  Row,
  Col,
  Tooltip,
  Empty,
  Pagination
} from 'antd';
import {
  DatabaseOutlined,
  FileTextOutlined,
  SearchOutlined,
  EyeOutlined,
  ReloadOutlined,
  BarChartOutlined,
  FolderOpenOutlined
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { documentsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const ChunksViewer = React.memo(() => {
  const { user } = useAuth();
  
  // State management
  const [chunks, setChunks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statsLoading, setStatsLoading] = useState(false);
  
  // Pagination
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true,
    pageSizeOptions: ['10', '20', '50', '100']
  });
  
  // Filters
  const [filters, setFilters] = useState({
    fileName: null,
    searchText: ''
  });
  
  // Modal for content preview
  const [previewModal, setPreviewModal] = useState({
    visible: false,
    chunk: null,
    showMarkdown: false
  });

  // Load chunks data
  const loadChunks = async (page = 1, pageSize = 20) => {
    setLoading(true);
    try {
      const offset = (page - 1) * pageSize;
      const params = {
        limit: pageSize,
        offset: offset
      };
      
      // Add file filter if specified
      if (filters.fileName) {
        params.file_name = filters.fileName;
      }
      
      const response = await documentsAPI.getChunks(params);
      
      setChunks(response.chunks || []);
      setPagination(prev => ({
        ...prev,
        current: page,
        pageSize: pageSize,
        total: response.total || 0
      }));
      
    } catch (error) {
      console.error('Error loading chunks:', error);
      setChunks([]);
    } finally {
      setLoading(false);
    }
  };

  // Load statistics
  const loadStats = async () => {
    setStatsLoading(true);
    try {
      const response = await documentsAPI.getChunksStats();
      setStats(response);
    } catch (error) {
      console.error('Error loading stats:', error);
      setStats(null);
    } finally {
      setStatsLoading(false);
    }
  };

  // Initial data load
  useEffect(() => {
    loadChunks();
    loadStats();
  }, []);

  // Reload data when filters change
  useEffect(() => {
    loadChunks(1, pagination.pageSize);
  }, [filters.fileName]);

  // Handle pagination changes
  const handleTableChange = (paginationConfig) => {
    loadChunks(paginationConfig.current, paginationConfig.pageSize);
  };

  // Handle refresh
  const handleRefresh = () => {
    loadChunks(pagination.current, pagination.pageSize);
    loadStats();
  };

  // Filter chunks by search text
  const filteredChunks = chunks.filter(chunk => 
    !filters.searchText || 
    chunk.title?.toLowerCase().includes(filters.searchText.toLowerCase()) ||
    chunk.file_name?.toLowerCase().includes(filters.searchText.toLowerCase()) ||
    chunk.section?.toLowerCase().includes(filters.searchText.toLowerCase()) ||
    chunk.content?.toLowerCase().includes(filters.searchText.toLowerCase())
  );

  // Get unique file names for filter
  const uniqueFileNames = [...new Set(chunks.map(chunk => chunk.file_name))].sort();

  // Table columns configuration
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: (a, b) => a.id - b.id,
    },
    {
      title: 'File Name',
      dataIndex: 'file_name',
      key: 'file_name',
      width: 200,
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Tag icon={<FileTextOutlined />} color="blue">
            {text}
          </Tag>
        </Tooltip>
      ),
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: 250,
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <Text strong>{text}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Section',
      dataIndex: 'section',
      key: 'section',
      width: 200,
      ellipsis: true,
      render: (text) => text || <Text type="secondary">No section</Text>,
    },
    {
      title: 'Content Preview',
      dataIndex: 'content_preview',
      key: 'content_preview',
      width: 300,
      ellipsis: true,
      render: (text) => (
        <Text type="secondary" style={{ fontSize: '12px' }}>
          {text}
        </Text>
      ),
    },
    {
      title: 'Length',
      dataIndex: 'content_length',
      key: 'content_length',
      width: 100,
      sorter: (a, b) => a.content_length - b.content_length,
      render: (length) => (
        <Tag color={length > 1000 ? 'red' : length > 500 ? 'orange' : 'green'}>
          {length} chars
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            size="small"
            onClick={() => setPreviewModal({ visible: true, chunk: record, showMarkdown: false })}
            title="Preview full content"
          />
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', backgroundColor: '#faf7f2' }}>
      <Card 
        style={{ 
          marginBottom: '24px',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          border: '1px solid #e8dcc0'
        }}
      >
        <Row gutter={[24, 16]} align="middle">
          <Col flex="auto">
            <Space align="center" size={16}>
              <DatabaseOutlined style={{ fontSize: '24px', color: '#D2691E' }} />
              <div>
                <Title level={3} style={{ margin: 0, color: '#6B3410' }}>
                  📊 Vector Database Chunks
                </Title>
                <Text type="secondary">
                  Manage and view all chunks stored in Milvus vector database
                </Text>
              </div>
            </Space>
          </Col>
          <Col>
            <Button 
              type="primary"
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              loading={loading || statsLoading}
              style={{ 
                backgroundColor: '#D2691E',
                borderColor: '#D2691E',
                borderRadius: '6px'
              }}
            >
              Refresh
            </Button>
          </Col>
        </Row>
      </Card>

      {/* Statistics Cards */}
      {stats && (
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" style={{ textAlign: 'center', borderRadius: '8px' }}>
              <Statistic
                title="Total Chunks"
                value={stats.total_chunks}
                prefix={<DatabaseOutlined style={{ color: '#D2691E' }} />}
                valueStyle={{ color: '#D2691E' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" style={{ textAlign: 'center', borderRadius: '8px' }}>
              <Statistic
                title="Documents"
                value={stats.total_documents}
                prefix={<FileTextOutlined style={{ color: '#B8860B' }} />}
                valueStyle={{ color: '#B8860B' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" style={{ textAlign: 'center', borderRadius: '8px' }}>
              <Statistic
                title="Avg Chunks/Doc"
                value={stats.avg_chunks_per_document}
                prefix={<BarChartOutlined style={{ color: '#CD853F' }} />}
                valueStyle={{ color: '#CD853F' }}
                precision={1}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card size="small" style={{ textAlign: 'center', borderRadius: '8px' }}>
              <Statistic
                title="File Types"
                value={Object.keys(stats.file_types || {}).length}
                prefix={<FolderOpenOutlined style={{ color: '#A0522D' }} />}
                valueStyle={{ color: '#A0522D' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Filters */}
      <Card 
        size="small" 
        style={{ 
          marginBottom: '16px',
          borderRadius: '8px',
          backgroundColor: '#fdf9f3'
        }}
      >
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={12} md={8}>
            <Input
              placeholder="🔍 Search in title, content, section..."
              prefix={<SearchOutlined />}
              value={filters.searchText}
              onChange={(e) => setFilters(prev => ({ ...prev, searchText: e.target.value }))}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={8}>
            <Select
              placeholder="Filter by file name"
              value={filters.fileName}
              onChange={(value) => setFilters(prev => ({ ...prev, fileName: value }))}
              allowClear
              style={{ width: '100%' }}
            >
              {uniqueFileNames.map(fileName => (
                <Option key={fileName} value={fileName}>
                  📄 {fileName}
                </Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={24} md={8}>
            <Space>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                Showing {filteredChunks.length} of {pagination.total} chunks
              </Text>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Main Table */}
      <Card 
        style={{ 
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          border: '1px solid #e8dcc0'
        }}
      >
        {filteredChunks.length === 0 && !loading ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <div>
                <Text type="secondary">No chunks found in vector database</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  Upload some documents to see chunks here
                </Text>
              </div>
            }
          />
        ) : (
          <Table
            columns={columns}
            dataSource={filteredChunks}
            loading={loading}
            pagination={pagination}
            onChange={handleTableChange}
            rowKey="id"
            size="middle"
            scroll={{ x: 1200 }}
            style={{ 
              backgroundColor: 'white',
            }}
            rowClassName={(record, index) => 
              index % 2 === 0 ? 'table-row-light' : 'table-row-dark'
            }
          />
        )}
      </Card>

      {/* Preview Modal */}
      <Modal
        title={
          <Space>
            <EyeOutlined style={{ color: '#D2691E' }} />
            <span>Chunk Content Preview</span>
          </Space>
        }
        open={previewModal.visible}
        onCancel={() => setPreviewModal({ visible: false, chunk: null, showMarkdown: false })}
        footer={[
          <Button 
            key="close"
            onClick={() => setPreviewModal({ visible: false, chunk: null, showMarkdown: false })}
          >
            Close
          </Button>
        ]}
        width={800}
      >
        {previewModal.chunk && (
          <div>
            <Row gutter={[16, 16]} style={{ marginBottom: '16px' }}>
              <Col span={8}>
                <Text strong>File:</Text>
                <br />
                <Tag color="blue">{previewModal.chunk.file_name}</Tag>
              </Col>
              <Col span={8}>
                <Text strong>Chunk ID:</Text>
                <br />
                <Tag color="green">{previewModal.chunk.id}</Tag>
              </Col>
              <Col span={8}>
                <Text strong>Length:</Text>
                <br />
                <Tag color="orange">{previewModal.chunk.content_length} chars</Tag>
              </Col>
            </Row>
            
            <div style={{ marginBottom: '16px' }}>
              <Text strong>Title:</Text>
              <div style={{ 
                padding: '8px 12px', 
                backgroundColor: '#f9f9f9', 
                borderRadius: '4px',
                marginTop: '4px'
              }}>
                {previewModal.chunk.title}
              </div>
            </div>
            
            {previewModal.chunk.section && (
              <div style={{ marginBottom: '16px' }}>
                <Text strong>Section:</Text>
                <div style={{ 
                  padding: '8px 12px', 
                  backgroundColor: '#f9f9f9', 
                  borderRadius: '4px',
                  marginTop: '4px'
                }}>
                  {previewModal.chunk.section}
                </div>
              </div>
            )}
            
            <div>
              <Text strong>Content:</Text>
              <div style={{ marginTop: '8px' }}>
                {/* Raw Content Tab */}
                <div style={{ marginBottom: '16px' }}>
                  <Space>
                    <Button
                      size="small"
                      type={previewModal.showMarkdown ? 'default' : 'primary'}
                      onClick={() => setPreviewModal(prev => ({ ...prev, showMarkdown: false }))}
                    >
                      📝 Raw Text
                    </Button>
                    <Button
                      size="small"
                      type={previewModal.showMarkdown ? 'primary' : 'default'}
                      onClick={() => setPreviewModal(prev => ({ ...prev, showMarkdown: true }))}
                    >
                      📋 Markdown Preview
                    </Button>
                  </Space>
                </div>

                {previewModal.showMarkdown ? (
                  /* Markdown Rendered View */
                  <div
                    style={{
                      border: '1px solid #d9d9d9',
                      borderRadius: '6px',
                      padding: '12px',
                      backgroundColor: '#fafafa',
                      maxHeight: '400px',
                      overflowY: 'auto',
                      fontFamily: 'inherit',
                      fontSize: '14px',
                      lineHeight: '1.6'
                    }}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        // Custom styling for markdown elements
                        h1: ({ children }) => (
                          <h1 style={{ 
                            fontSize: '1.5em', 
                            fontWeight: 'bold', 
                            margin: '16px 0 12px 0', 
                            color: '#2c3e50',
                            borderBottom: '2px solid #D2691E'
                          }}>
                            {children}
                          </h1>
                        ),
                        h2: ({ children }) => (
                          <h2 style={{ 
                            fontSize: '1.3em', 
                            fontWeight: 'bold', 
                            margin: '14px 0 10px 0', 
                            color: '#34495e'
                          }}>
                            {children}
                          </h2>
                        ),
                        h3: ({ children }) => (
                          <h3 style={{ 
                            fontSize: '1.2em', 
                            fontWeight: 'bold', 
                            margin: '12px 0 8px 0', 
                            color: '#5d6d7e'
                          }}>
                            {children}
                          </h3>
                        ),
                        h4: ({ children }) => (
                          <h4 style={{ 
                            fontSize: '1.1em', 
                            fontWeight: 'bold', 
                            margin: '10px 0 6px 0', 
                            color: '#6c757d'
                          }}>
                            {children}
                          </h4>
                        ),
                        p: ({ children }) => (
                          <p style={{ 
                            margin: '8px 0', 
                            lineHeight: '1.6'
                          }}>
                            {children}
                          </p>
                        ),
                        ul: ({ children }) => (
                          <ul style={{ 
                            paddingLeft: '20px', 
                            margin: '8px 0'
                          }}>
                            {children}
                          </ul>
                        ),
                        ol: ({ children }) => (
                          <ol style={{ 
                            paddingLeft: '20px', 
                            margin: '8px 0'
                          }}>
                            {children}
                          </ol>
                        ),
                        li: ({ children }) => (
                          <li style={{ margin: '4px 0' }}>
                            {children}
                          </li>
                        ),
                        blockquote: ({ children }) => (
                          <blockquote style={{
                            borderLeft: '4px solid #D2691E',
                            paddingLeft: '16px',
                            margin: '12px 0',
                            fontStyle: 'italic',
                            backgroundColor: '#fdf9f3'
                          }}>
                            {children}
                          </blockquote>
                        ),
                        code: ({ children, inline }) => (
                          inline ? (
                            <code style={{
                              backgroundColor: '#f1f1f1',
                              padding: '2px 4px',
                              borderRadius: '3px',
                              fontFamily: 'Monaco, Consolas, monospace',
                              fontSize: '0.9em'
                            }}>
                              {children}
                            </code>
                          ) : (
                            <pre style={{
                              backgroundColor: '#f8f8f8',
                              padding: '12px',
                              borderRadius: '6px',
                              overflow: 'auto',
                              fontFamily: 'Monaco, Consolas, monospace',
                              fontSize: '0.9em',
                              border: '1px solid #e1e1e1'
                            }}>
                              <code>{children}</code>
                            </pre>
                          )
                        ),
                        table: ({ children }) => (
                          <table style={{
                            borderCollapse: 'collapse',
                            width: '100%',
                            margin: '12px 0'
                          }}>
                            {children}
                          </table>
                        ),
                        th: ({ children }) => (
                          <th style={{
                            border: '1px solid #ddd',
                            padding: '8px 12px',
                            backgroundColor: '#f2f2f2',
                            fontWeight: 'bold',
                            textAlign: 'left'
                          }}>
                            {children}
                          </th>
                        ),
                        td: ({ children }) => (
                          <td style={{
                            border: '1px solid #ddd',
                            padding: '8px 12px'
                          }}>
                            {children}
                          </td>
                        )
                      }}
                    >
                      {previewModal.chunk.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  /* Raw Text View */
                  <TextArea
                    value={previewModal.chunk.content}
                    rows={15}
                    readOnly
                    style={{ 
                      fontFamily: 'Monaco, Consolas, monospace',
                      fontSize: '13px',
                      resize: 'none',
                      backgroundColor: '#f8f9fa'
                    }}
                  />
                )}
              </div>
            </div>
          </div>
        )}
      </Modal>

      <style jsx>{`
        .table-row-light {
          background-color: #ffffff;
        }
        .table-row-dark {
          background-color: #fdfcfa;
        }
        .ant-table-tbody > tr:hover > td {
          background-color: #fff7e6 !important;
        }
      `}</style>
    </div>
  );
});

export default ChunksViewer;
