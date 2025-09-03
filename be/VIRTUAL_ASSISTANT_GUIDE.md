# 🤖 Hướng dẫn Trợ lý ảo DVC.AI

## Tổng quan

DVC.AI là hệ thống trợ lý ảo thông minh được xây dựng với:
- **RAG (Retrieval-Augmented Generation)** với Milvus Vector Database
- **Langraph** cho workflow management và conversation flow  
- **Conversation Memory** với MongoDB storage
- **Real-time WebSocket** communication
- **OpenAI API** integration (GPT-4o + text-embedding-3-large)

## 🏗️ Kiến trúc hệ thống

```
Frontend (React)
    ↓ WebSocket/HTTP
Backend FastAPI
    ↓
Virtual Assistant Service (Langraph)
    ↓
┌─────────────────┬─────────────────┐
│   RAG Service   │ Conversation    │
│   (Milvus +     │ Memory Service  │
│   OpenAI)       │ (MongoDB)       │
└─────────────────┴─────────────────┘
```

## 🚀 Cài đặt và Chạy

### 1. Cài đặt Dependencies mới

```bash
cd be
pip install -r requirements.txt

# Dependencies chính được thêm:
# - langgraph>=0.1.0
# - langchain-openai>=0.1.0  
# - faiss-cpu>=1.7.0
```

### 2. Cấu hình Environment Variables

Trong file `.env`:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB (cho Conversation Memory)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=dvc_ai_db

# Milvus (cho Vector Database)
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Existing configs...
SECRET_KEY=your-secret-key
```

### 3. Khởi động Services

```bash
# Terminal 1: Start MongoDB (Docker)
docker-compose -f docker/docker-compose-mongodb.yml up -d

# Terminal 2: Start Milvus (Docker)  
docker-compose -f docker/docker-compose-milvus.yml up -d

# Terminal 3: Start Redis
python scripts/start_redis.py

# Terminal 4: Start Celery Worker
python scripts/start_worker.py

# Terminal 5: Start Backend API
python main.py

# Terminal 6: Start Frontend
cd ../fe && npm start
```

### 4. Load Documents vào Milvus

```bash
cd be
python scripts/load_documents_to_milvus.py
```

## 🧪 Testing

### Test Virtual Assistant

```bash
cd be
python scripts/test_virtual_assistant.py
```

Test script sẽ kiểm tra:
- ✅ Basic conversation flow
- ✅ RAG service functionality  
- ✅ Conversation memory
- ✅ Langraph workflow
- ✅ Session management

### Verify Embedding Model

```bash
cd be
python scripts/verify_embedding_model.py
```

Verification script sẽ kiểm tra:
- ✅ OpenAI text-embedding-3-large configuration
- ✅ Vector dimension (3072)
- ✅ Embedding generation test
- ✅ RAG service integration

### Test qua API

```bash
# Test chatbot endpoint
curl -X POST "http://localhost:8001/api/chatbot/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Thủ tục làm căn cước công dân như thế nào?", "session_id": "test123"}'

# Test status
curl -X GET "http://localhost:8001/api/chatbot/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 API Endpoints mới

### Chatbot API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chatbot/message` | Gửi tin nhắn đến trợ lý ảo |
| GET | `/api/chatbot/session/{session_id}` | Lấy thông tin session |
| GET | `/api/chatbot/history/{session_id}` | Lấy lịch sử conversation |
| POST | `/api/chatbot/session/new` | Tạo session mới |
| GET | `/api/chatbot/sessions` | Lấy danh sách sessions của user |
| GET | `/api/chatbot/status` | Trạng thái hệ thống |
| POST | `/api/chatbot/cleanup` | Dọn dẹp sessions cũ (admin) |

### WebSocket Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `chat_message` | Client → Server | Gửi tin nhắn real-time |
| `chat_response` | Server → Client | Phản hồi từ trợ lý ảo |
| `typing` | Server → Client | Typing indicator |
| `join_chat_session` | Client → Server | Tham gia session |
| `get_chat_history` | Client → Server | Lấy lịch sử chat |

## 🧠 Conversation Memory

### Tính năng

- **Persistent Storage**: Lưu trữ conversation trong MongoDB
- **Session Management**: Quản lý sessions theo user  
- **Context Preservation**: Giữ ngữ cảnh giữa các tin nhắn
- **Automatic Cleanup**: Tự động dọn dẹp sessions cũ
- **Fallback Support**: Fallback to in-memory nếu MongoDB không khả dụng

### Usage trong Code

```python
from app.services.conversation_memory import conversation_memory

# Lưu tin nhắn
conversation_memory.save_message(
    session_id="session123",
    user_id="user456", 
    message=HumanMessage(content="Xin chào"),
    metadata={"timestamp": "2024-01-01T00:00:00"}
)

# Lấy lịch sử
history = conversation_memory.get_conversation_history("session123", limit=10)

# Lấy thông tin session
context = conversation_memory.get_session_context("session123")
```

## 🔍 RAG Service với Milvus

### Workflow

1. **Document Indexing**: Documents được chunk và embed bằng OpenAI
2. **Vector Storage**: Embeddings lưu trong Milvus
3. **Semantic Search**: Tìm kiếm documents liên quan
4. **Context Generation**: Format context cho LLM
5. **Response Generation**: Sinh phản hồi với OpenAI

### Configuration

```python
# Trong RAGService  
top_k = 5  # Số documents retrieve
max_context_length = 4000  # Độ dài context tối đa
embedding_model = "text-embedding-3-large"  # OpenAI best embedding model
chat_model = "gpt-4o"  # OpenAI latest chat model
```

### OpenAI text-embedding-3-large Features

- **Vector Dimension**: 3072 (cao nhất trong OpenAI models)
- **Performance**: Accuracy cao nhất cho semantic search
- **Language Support**: Hỗ trợ tiếng Việt và đa ngôn ngữ
- **Cost**: Cao hơn text-embedding-3-small nhưng chất lượng tốt hơn
- **Use Case**: Optimal cho production RAG systems

```env
# Environment configuration
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4o
OPENAI_API_KEY=your_openai_api_key_here
```

## 🌊 Langraph Workflow

### State Management

```python
class AssistantState:
    messages: List[BaseMessage]
    session_id: str
    user_id: str
    context: Dict[str, Any] 
    rag_results: Optional[Dict[str, Any]]
    needs_search: bool
```

### Workflow Nodes

1. **analyze_query**: Phân tích câu hỏi để quyết định có cần RAG không
2. **search_knowledge**: Tìm kiếm thông tin từ knowledge base
3. **generate_response**: Sinh phản hồi từ LLM
4. **save_context**: Lưu conversation context

### Conditional Logic

```python
def _should_search(state: AssistantState) -> str:
    return "search" if state.needs_search else "direct"
```

## 🎨 Frontend Features

### Theme & UI

- **Orange-brown color scheme**: `#D2691E` (primary), `#DEB887` (light)
- **MaisonNeue font**: Custom font theo brand identity
- **Responsive design**: Mobile-first approach
- **Real-time indicators**: Typing, connection status

### WebSocket Integration

```javascript
// Kết nối WebSocket
websocketService.connect(user.username);

// Gửi tin nhắn real-time  
websocketService.sendChatMessage(message, sessionId);

// Lắng nghe phản hồi
websocketService.on('chat_response', handleChatResponse);
```

### Session Management

- **Session ID**: Unique identifier cho mỗi conversation
- **Connection Status**: Hiển thị real-time/HTTP mode
- **Message Metadata**: RAG confidence, sources, timestamp

## 📊 Monitoring & Analytics

### Conversation Metrics

```python
# Session statistics
session_info = virtual_assistant.get_session_info(session_id)
# {
#   "session_id": "...",
#   "message_count": 15,
#   "last_activity": "2024-01-01T10:30:00",
#   "rag_connected": true
# }

# RAG performance
rag_stats = rag_service.get_stats()
# {
#   "collection_size": 1000,
#   "embedding_model": "text-embedding-3-large",
#   "chat_model": "gpt-4o-mini"
# }
```

### Active Sessions

```python
active_sessions = conversation_memory.get_active_sessions(user_id="admin")
```

## 🔧 Troubleshooting

### Common Issues

1. **Langraph import error**: `pip install langgraph>=0.1.0`
2. **Milvus connection failed**: Check Docker containers running
3. **MongoDB not connected**: Check fallback to in-memory mode  
4. **OpenAI API error**: Verify API key in environment
5. **WebSocket disconnection**: Check CORS configuration

### Debug Commands

```bash
# Check services status
python scripts/test_virtual_assistant.py

# Test RAG only
python scripts/test_rag_system.py

# Check MongoDB connection
python -c "from app.services.conversation_memory import conversation_memory; print(conversation_memory.connected)"

# Check Milvus connection  
python -c "from app.services.rag_service import RAGService; r=RAGService(); print(r.connect_milvus())"
```

### Log Levels

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # For detailed debugging
```

## 🚀 Production Deployment

### Performance Optimization

1. **Connection Pooling**: MongoDB và Milvus connections
2. **Caching**: Redis cache cho frequent queries  
3. **Load Balancing**: Multiple FastAPI instances
4. **Resource Limits**: Memory limits cho conversation history

### Security

1. **Authentication**: JWT tokens cho API access
2. **Rate Limiting**: Prevent spam/abuse
3. **Input Validation**: Sanitize user inputs
4. **CORS**: Proper CORS configuration

### Monitoring

1. **Health Checks**: `/api/chatbot/status` endpoint
2. **Metrics**: Conversation success rates, response times
3. **Alerting**: Failed connections, API errors
4. **Logging**: Structured logging với correlation IDs

## 📈 Future Enhancements

- [ ] **Multi-language Support**: Supports English, Vietnamese
- [ ] **Voice Interface**: Speech-to-text integration  
- [ ] **Advanced Analytics**: Conversation insights, user behavior
- [ ] **Custom Models**: Fine-tuned models cho domain-specific tasks
- [ ] **Plugin System**: Extensible architecture for new features
- [ ] **Admin Dashboard**: Management interface for conversations

## 📞 Support

- **Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/api/chatbot/status  
- **Test Suite**: `python scripts/test_virtual_assistant.py`
- **GitHub Issues**: Repository issue tracker

---

**Version**: 3.2.0  
**Last Updated**: September 2025  
**Technologies**: FastAPI + Langraph + RAG + Milvus + OpenAI API  
**Status**: ✅ Production Ready
