# Enhanced Virtual Assistant với Agent Architecture

## 🎯 Tổng quan

Hệ thống đã được tái cấu trúc hoàn toàn theo kiến trúc **modular node-based** sử dụng **LangGraph**, dựa trên mô hình từ `example/src`. Điều này mang lại:

- **Intelligent Routing**: Tự động phân loại query (casual vs RAG)
- **Modular Architecture**: Các nodes chuyên biệt cho từng chức năng
- **Advanced RAG Pipeline**: Transform → Retrieve → Generate → PostProcess
- **Citation Support**: Trích dẫn nguồn tài liệu trong response
- **Context Awareness**: Hiểu ngữ cảnh cuộc trò chuyện

## 🏗️ Kiến trúc Hệ thống

### 1. State Management
```python
# InputState: Interface đầu vào
- messages: Lịch sử cuộc trò chuyện
- session_id: ID phiên
- user_id: ID người dùng
- memories: Thông tin bổ sung

# ChatState: State cho RAG workflow
- better_query: Query đã được tối ưu
- documents: Tài liệu tìm được
- generation: Response được tạo
- confidence: Độ tin cậy
```

### 2. Node Architecture

#### Routing Nodes
- **AnalyzeQueryNode**: Phân tích query và quyết định routing

#### Transform Nodes  
- **TransformQueryNode**: Cải thiện query dựa trên context

#### Retrieval Nodes
- **RetrieveNode**: Tìm kiếm documents từ Milvus
- **CachedDocumentsNode**: Kiểm tra cache (future enhancement)

#### Generation Nodes
- **ContextGeneratorNode**: Tạo response với citations
- **GenericResponseNode**: Response đơn giản cho casual chat
- **PostProcessNode**: Xử lý cuối và format kết quả

### 3. Graph Workflows

#### Main Graph
```
Query → Analyze → [Route] → RAG/Generic → Response
```

#### RAG Graph  
```
Transform → Cache → Retrieve → [Check] → Generate → PostProcess
```

## 🚀 Sử dụng

### 1. API Endpoints

#### Enhanced Chatbot API
```bash
# Gửi tin nhắn
POST /api/v1/enhanced-chatbot/message
{
  "message": "Thủ tục đăng ký thường trú như thế nào?",
  "session_id": "optional"
}

# Kiểm tra status
GET /api/v1/enhanced-chatbot/status

# Lấy thông tin session
GET /api/v1/enhanced-chatbot/session/{session_id}

# Lấy lịch sử
GET /api/v1/enhanced-chatbot/history/{session_id}
```

### 2. Response Format

```json
{
  "response": "Để đăng ký thường trú, bạn cần...",
  "session_id": "abc123",
  "timestamp": "2024-01-01T10:00:00",
  "metadata": {
    "rag_used": true,
    "confidence": 0.85,
    "extracted_entities": ["1", "2"],
    "source_info": "Nguồn tham khảo:\n1. Tài liệu A...",
    "response_type": "rag"
  }
}
```

### 3. Testing

```bash
# Chạy test script
cd be
python scripts/test_enhanced_agent.py
```

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI
OPENAI_API_KEY=your_key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### Agent Configuration
```python
# be/app/agent/configuration.py
@dataclass
class Configuration:
    temperature: float = 0.7
    max_tokens: int = 2000
    max_search_results: int = 5
    search_threshold: float = 0.7
    retriever_provider: str = "milvus"
```

## 📊 Monitoring & Debugging

### 1. Logs
```bash
# Xem logs chi tiết
tail -f app.log | grep "Enhanced"
```

### 2. Status Endpoint
```bash
curl http://localhost:8001/api/v1/enhanced-chatbot/status
```

### 3. Debug Information
- Routing decisions logged
- Document retrieval metrics
- Generation process tracking
- Error handling với traceback

## 🆚 So sánh với Hệ thống Cũ

| Tính năng | Cũ | Mới (Enhanced) |
|-----------|----|-----------------| 
| Architecture | Monolithic | Modular Nodes |
| Routing | Simple keyword | AI-powered routing |
| RAG Pipeline | Basic | Multi-stage with transform |
| Citations | None | Full citation support |
| Context Awareness | Limited | Advanced context handling |
| Error Handling | Basic | Comprehensive with fallbacks |
| Testing | Manual | Automated test suite |

## 🔄 Migration Guide

### Để chuyển từ hệ thống cũ:

1. **API Endpoints**: Thay `/chatbot/` → `/enhanced-chatbot/`
2. **Response Format**: Kiểm tra metadata mới
3. **Configuration**: Cập nhật config nếu cần
4. **Testing**: Sử dụng test script để verify

### Backward Compatibility
- Hệ thống cũ vẫn hoạt động qua `/chatbot/`
- Có thể chạy song song trong quá trình migration
- Frontend có thể chọn endpoint phù hợp

## 🎛️ Tuning & Optimization

### 1. Routing Threshold
```python
# Điều chỉnh trong prompts.py
ROUTER_PROMPT = """..."""
```

### 2. RAG Parameters
```python
# Trong configuration.py
max_search_results: int = 5  # Số documents
search_threshold: float = 0.7  # Ngưỡng relevance
```

### 3. Response Quality
```python
# Trong generation nodes
temperature: float = 0.7  # Creativity vs accuracy
max_tokens: int = 2000   # Response length
```

## 🚨 Troubleshooting

### Common Issues

1. **Milvus Connection Failed**
   ```bash
   # Kiểm tra Milvus
   docker ps | grep milvus
   ```

2. **OpenAI API Errors**
   ```bash
   # Kiểm tra API key
   echo $OPENAI_API_KEY
   ```

3. **Routing Issues**
   ```bash
   # Test routing riêng
   python scripts/test_enhanced_agent.py
   ```

### Performance Issues

1. **Slow Response**: Giảm `max_search_results`
2. **Memory Usage**: Điều chỉnh conversation history limit
3. **API Rate Limits**: Implement caching

## 📈 Future Enhancements

- [ ] Document caching system
- [ ] Multi-language support expansion  
- [ ] Advanced conversation memory
- [ ] Custom tool integration
- [ ] Real-time learning capabilities
