# 🏗️ DVC.AI System Architecture

## 🎯 **Overview**

DVC.AI is built with a modern **microservice architecture** featuring:
- 🤖 **LangGraph Agent** - Advanced AI workflow management
- 📚 **RAG Pipeline** - Retrieval-Augmented Generation with vector search
- 🏗️ **Modular Design** - Separation of concerns, scalable components
- 🔄 **Real-time Communication** - WebSocket integration
- 🐳 **Containerized Deployment** - Docker-based microservices

---

## 📊 **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Users/Admins  │
│   (React.js)    │    │                 │
└─────────┬───────┘    └─────────┬───────┘
          │ HTTP/WebSocket         │ HTTP
          │                       │
┌─────────▼─────────────────────────▼──────┐
│           API Gateway (FastAPI)          │
│          + WebSocket Manager             │
└─────────┬─────────────────────────┬──────┘
          │                         │
┌─────────▼──────┐         ┌────────▼─────┐
│ Authentication │         │   Document   │
│    Service     │         │   Service    │
└─────────┬──────┘         └────────┬─────┘
          │                         │
┌─────────▼─────────────────────────▼──────┐
│         Virtual Assistant Core           │
│     (LangGraph + RAG Pipeline)           │
└─────────┬─────────────────────────┬──────┘
          │                         │
┌─────────▼──────┐         ┌────────▼─────┐
│  Vector Search │         │  Conversation│
│   (Milvus)     │         │   Memory     │
│                │         │  (MongoDB)   │
└────────────────┘         └──────────────┘
```

---

## 🧩 **Microservice Components**

### **1. Frontend Service**
- **Technology**: React.js + Custom CSS + MaisonNeue font
- **Responsibilities**: 
  - User interface rendering
  - Real-time chat interface
  - Document management UI
  - Authentication flow

### **2. API Gateway (FastAPI)**
- **Entry Point**: All client requests
- **Features**:
  - Request routing
  - Authentication middleware
  - WebSocket management
  - CORS handling

### **3. Authentication Service**
```python
# app/api/auth.py + app/core/security.py
- JWT token management
- User session handling  
- Role-based access control
- Password hashing
```

### **4. Document Service**
```python
# app/api/documents.py + app/services/gcs_service.py
- File upload/download
- Document processing
- Metadata management
- Cloud storage integration
```

### **5. Virtual Assistant Core**
```python
# app/agent/ - LangGraph Agent Architecture
- Intelligent query routing
- RAG pipeline orchestration
- Conversation state management
- Response generation
```

---

## 🤖 **LangGraph Agent Architecture**

### **Agent Workflow**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   User      │    │  Analyze    │    │ Route       │
│   Query     │───▶│  Query      │───▶│ Decision    │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
                   ┌────▼────┐         ┌─────▼──────┐       ┌──────▼─────┐
                   │ Casual  │         │    RAG     │       │   Complex  │
                   │  Chat   │         │  Pipeline  │       │  Research  │
                   └────┬────┘         └─────┬──────┘       └──────┬─────┘
                        │                    │                     │
                   ┌────▼────┐         ┌─────▼──────┐       ┌──────▼─────┐
                   │Generic  │         │ Retrieve   │       │Multi-step  │
                   │Response │         │Documents   │       │ Planning   │
                   └────┬────┘         └─────┬──────┘       └──────┬─────┘
                        │                    │                     │
                        └────────────────────┼─────────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │ Post Process &  │
                                    │ Format Response │
                                    └─────────────────┘
```

### **Node Architecture**

#### **Routing Nodes**
```python
# app/agent/nodes/analyze_query.py
class AnalyzeQueryNode:
    """Phân tích query và quyết định routing"""
    def analyze_intent(self, query: str) -> RoutingDecision
    def extract_context(self, messages: List[Message]) -> Context
```

#### **Transform Nodes**
```python
# app/agent/nodes/transform_query.py  
class TransformQueryNode:
    """Cải thiện query dựa trên context"""
    def enhance_query(self, query: str, context: Context) -> str
    def add_conversation_context(self, query: str) -> str
```

#### **Retrieval Nodes**
```python
# app/agent/nodes/retrieve.py
class RetrieveNode:
    """Tìm kiếm documents từ Milvus"""
    def semantic_search(self, query: str) -> List[Document]
    def rerank_results(self, documents: List[Document]) -> List[Document]
```

#### **Generation Nodes**
```python
# app/agent/nodes/context_generator.py
class ContextGeneratorNode:
    """Tạo response với citations"""
    def generate_with_context(self, query: str, docs: List[Document]) -> Response
    def add_citations(self, response: str, sources: List[Document]) -> str

# app/agent/nodes/generic_response.py  
class GenericResponseNode:
    """Response đơn giản cho casual chat"""
    def generate_casual_response(self, query: str) -> Response
```

### **State Management**
```python
# app/agent/state.py
class InputState(TypedDict):
    messages: List[BaseMessage]
    session_id: str
    user_id: Optional[str]
    memories: Dict[str, Any]

class ChatState(InputState):
    better_query: str
    documents: List[Document]
    generation: str
    confidence: float
```

---

## 📚 **RAG Pipeline Architecture**

### **Pipeline Flow**
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Query     │    │ Transform   │    │  Vector     │
│ Processing  │───▶│   Query     │───▶│  Search     │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                              │
┌─────────────┐    ┌─────────────┐    ┌──────▼──────┐
│  Response   │    │ Generate    │    │  Retrieve   │
│ Formation   │◀───│ Response    │◀───│ Documents   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### **Components**

#### **1. Document Processing**
```python
# app/utils/document_processor.py
class DocumentProcessor:
    def chunk_documents(self, content: str) -> List[Chunk]
    def extract_metadata(self, file_path: str) -> DocumentMetadata
    def process_markdown(self, content: str) -> ProcessedDocument
```

#### **2. Vector Search**
```python
# app/services/milvus_service.py
class MilvusService:
    def embed_query(self, query: str) -> List[float]
    def search_similar(self, embedding: List[float]) -> List[Document]
    def store_embeddings(self, documents: List[Document]) -> bool
```

#### **3. Response Generation**
```python
# app/services/rag_service.py
class RAGService:
    def retrieve_context(self, query: str) -> List[Document]
    def generate_response(self, query: str, context: List[Document]) -> Response
    def validate_response(self, response: Response) -> bool
```

---

## 🗄️ **Data Architecture**

### **MongoDB Collections**
```javascript
// Users collection
{
  _id: ObjectId,
  email: String,
  hashed_password: String,
  created_at: Date,
  last_login: Date
}

// Documents collection  
{
  _id: ObjectId,
  filename: String,
  file_size: Number,
  upload_date: Date,
  user_id: ObjectId,
  gcs_path: String,
  processed: Boolean
}

// Conversations collection
{
  _id: ObjectId,
  session_id: String,
  user_id: ObjectId,
  messages: [
    {
      role: String, // "user" | "assistant"
      content: String,
      timestamp: Date,
      metadata: Object
    }
  ],
  created_at: Date,
  updated_at: Date
}
```

### **Milvus Schema**
```python
# Collection: document_embeddings
{
  "id": DataType.INT64,           # Primary key
  "file_name": DataType.VARCHAR,  # Source document
  "content": DataType.VARCHAR,    # Text chunk
  "title": DataType.VARCHAR,      # Document title
  "section": DataType.VARCHAR,    # Section title  
  "embedding": DataType.FLOAT_VECTOR  # 3072-dim vector
}
```

---

## 🔄 **Communication Patterns**

### **HTTP API Pattern**
```python
# Request/Response cycle
Client ──HTTP──> API Gateway ──> Service ──> Database
                      │                         │
                      └── Response ←── Service ←┘
```

### **WebSocket Pattern**
```python
# Real-time communication
Client ──WebSocket──> WebSocket Manager ──> Agent ──> RAG Pipeline
   │                         │                            │
   └── Real-time updates ←────┴── Status updates ←────────┘
```

### **Background Tasks**
```python
# Celery pattern  
API ──> Queue ──> Worker ──> External Service
 │                  │            │
 └── Task ID ←──────┴── Result ←──┘
```

---

## 🔐 **Security Architecture**

### **Authentication Flow**
```
┌─────────┐    ┌─────────────┐    ┌─────────────┐
│  Login  │───▶│   Verify    │───▶│ Generate    │
│Request  │    │Credentials  │    │JWT Token    │
└─────────┘    └─────────────┘    └──────┬──────┘
                                          │
┌─────────┐    ┌─────────────┐    ┌──────▼──────┐
│Protected│◀───│   Verify    │◀───│ Send Token  │
│Resource │    │JWT Token    │    │to Client    │
└─────────┘    └─────────────┘    └─────────────┘
```

### **Access Control**
```python
# app/core/security.py
- JWT token validation
- Role-based permissions  
- API rate limiting
- CORS configuration
```

---

## 📈 **Scalability Considerations**

### **Horizontal Scaling**
- **Frontend**: Multiple replicas behind load balancer
- **Backend**: Stateless API servers
- **Database**: MongoDB replica sets
- **Vector DB**: Milvus cluster mode

### **Performance Optimization**
- **Caching**: Redis for session and query caching
- **CDN**: Static asset delivery
- **Connection pooling**: Database connections
- **Async processing**: Background tasks

### **Monitoring Points**
- API response times
- Database query performance  
- Vector search latency
- Memory usage patterns
- Error rates

---

## 🔮 **Future Enhancements**

### **Planned Features**
- **Multi-tenant support**: Organization isolation
- **Advanced analytics**: Usage tracking and insights
- **Plugin system**: Extensible agent capabilities
- **Voice interface**: Speech-to-text integration
- **Mobile app**: React Native companion

### **Architecture Evolution**
- **Event sourcing**: Audit trail and replay capability
- **CQRS pattern**: Command/Query responsibility segregation
- **Service mesh**: Enhanced inter-service communication
- **Kubernetes**: Container orchestration

---

*This architecture supports both current needs and future growth while maintaining code quality and system reliability.*
