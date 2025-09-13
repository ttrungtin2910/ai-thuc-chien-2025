# 🗄️ Database Architecture - DVC.AI

## 📊 **Database Overview**

DVC.AI sử dụng **hybrid database architecture** với:
- 🗄️ **MongoDB** - Document storage, user data, conversations
- 🔍 **Milvus** - Vector database cho semantic search và RAG
- 🔴 **Redis** - Caching, session storage, message queuing

---

## 🍃 **MongoDB Architecture**

### **Collections Structure**

#### **Users Collection**
```javascript
{
  _id: ObjectId("..."),
  email: "user@example.com",
  hashed_password: "$2b$12$...",
  created_at: ISODate("2024-01-01T00:00:00Z"),
  last_login: ISODate("2024-01-15T10:30:00Z"),
  role: "user", // "user" | "admin"
  is_active: true
}
```

#### **Documents Collection**
```javascript
{
  _id: ObjectId("..."),
  filename: "thutuc_congdan.pdf",
  original_filename: "Thủ tục công dân.pdf",
  file_size: 2048576,
  content_type: "application/pdf",
  upload_date: ISODate("2024-01-01T00:00:00Z"),
  user_id: ObjectId("..."),
  
  // Storage info
  local_path: "/uploads/documents/...",
  gcs_path: "gs://bucket/documents/...", // if GCS enabled
  
  // Processing status
  processed: true,
  processing_status: "completed", // "pending" | "processing" | "completed" | "failed"
  error_message: null,
  
  // Metadata
  page_count: 15,
  language: "vi",
  keywords: ["thủ tục", "công dân", "hành chính"],
  
  // Vector DB info
  milvus_collection: "document_embeddings",
  chunk_count: 45,
  embeddings_created: true
}
```

#### **Conversations Collection**
```javascript
{
  _id: ObjectId("..."),
  session_id: "sess_abc123...",
  user_id: ObjectId("..."),
  title: "Hỏi về thủ tục đăng ký thường trú",
  
  messages: [
    {
      role: "user", // "user" | "assistant" | "system"
      content: "Làm thế nào để đăng ký thường trú?",
      timestamp: ISODate("2024-01-01T10:00:00Z"),
      metadata: {
        client_ip: "192.168.1.100",
        user_agent: "Mozilla/5.0..."
      }
    },
    {
      role: "assistant",
      content: "Để đăng ký thường trú, bạn cần...",
      timestamp: ISODate("2024-01-01T10:00:15Z"),
      metadata: {
        sources: [
          {
            document_id: ObjectId("..."),
            chunk_id: 15,
            confidence: 0.85,
            citation: "Theo Thông tư 01/2023..."
          }
        ],
        processing_time: 2.5,
        model_used: "gpt-4",
        tokens_used: 450
      }
    }
  ],
  
  created_at: ISODate("2024-01-01T10:00:00Z"),
  updated_at: ISODate("2024-01-01T10:05:30Z"),
  
  // Analytics
  message_count: 8,
  total_tokens: 1250,
  user_satisfaction: null // future: rating system
}
```

### **MongoDB Indexes**
```javascript
// Users collection
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "created_at": -1 })
db.users.createIndex({ "last_login": -1 })

// Documents collection  
db.documents.createIndex({ "user_id": 1, "upload_date": -1 })
db.documents.createIndex({ "filename": 1 })
db.documents.createIndex({ "processed": 1, "processing_status": 1 })
db.documents.createIndex({ "keywords": 1 })

// Conversations collection
db.conversations.createIndex({ "session_id": 1 }, { unique: true })
db.conversations.createIndex({ "user_id": 1, "created_at": -1 })
db.conversations.createIndex({ "updated_at": -1 })
db.conversations.createIndex({ "messages.timestamp": -1 })
```

---

## 🔍 **Milvus Vector Database**

### **Collection Schema: document_embeddings**

```python
# Collection configuration
{
    "collection_name": "document_embeddings",
    "dimension": 3072,  # OpenAI text-embedding-3-large
    "metric_type": "IP",  # Inner Product
    "index_type": "IVF_FLAT",
    "nlist": 128
}
```

### **Field Structure**

| Field | Type | Max Length | Description | Example |
|-------|------|------------|-------------|---------|
| **id** | INT64 | - | Primary Key (Auto) | 12345 |
| **file_name** | VARCHAR | 512 | Source file name | `doc_congdan_1.000466.md` |
| **chunk_id** | INT64 | - | Unique chunk identifier | 0-99 (Section 1), 100-199 (Section 2) |
| **content** | VARCHAR | 8192 | Text content chunk | `"Thủ tục đăng ký thường trú..."` |
| **title** | VARCHAR | 512 | Document title from `# header` | `"Thủ tục hành chính công dân"` |
| **section** | VARCHAR | 512 | Section title from `## header` | `"Đăng ký thường trú"` |
| **embedding** | FLOAT_VECTOR | 3072 | OpenAI embedding vector | `[0.123, -0.456, ...]` |

### **Document Processing Pipeline**

#### **1. Document Ingestion**
```python
# Input: Markdown files from ../data/thutuccongdan/
def process_documents():
    files = load_markdown_files("../data/thutuccongdan/")
    for file in files:
        content = parse_markdown(file)
        chunks = chunk_content(content)
        embeddings = create_embeddings(chunks)
        store_in_milvus(embeddings)
```

#### **2. Content Chunking Strategy**

**Document Structure:**
```markdown
# Tiêu đề chính (title)
Nội dung mở đầu...

## Section 1 (section)  
Nội dung section 1...

## Section 2 (section)
Nội dung section 2...
```

**Chunking Logic:**
```python
# Section-based chunking
chunk_id_pattern = section_index * 100 + chunk_index

# Examples:
# Section 0: chunk_id 0, 1, 2, ...
# Section 1: chunk_id 100, 101, 102, ...
# Section 2: chunk_id 200, 201, 202, ...
```

#### **3. Embedding Generation**
```python
# OpenAI Configuration
model = "text-embedding-3-large"
dimensions = 3072
batch_size = 100

def create_embeddings(chunks):
    embeddings = []
    for batch in chunk_batches(chunks, batch_size):
        response = openai.embeddings.create(
            model=model,
            input=[chunk.content for chunk in batch],
            dimensions=dimensions
        )
        embeddings.extend(response.data)
    return embeddings
```

### **Search Operations**

#### **Semantic Search**
```python
def semantic_search(query: str, top_k: int = 5):
    # 1. Create query embedding
    query_embedding = openai.embeddings.create(
        model="text-embedding-3-large",
        input=query,
        dimensions=3072
    )
    
    # 2. Search in Milvus
    search_params = {
        "metric_type": "IP",
        "params": {"nprobe": 10}
    }
    
    results = collection.search(
        data=[query_embedding.data[0].embedding],
        anns_field="embedding", 
        param=search_params,
        limit=top_k,
        output_fields=["content", "title", "section", "file_name"]
    )
    
    return results
```

#### **Hybrid Search (Future)**
```python
def hybrid_search(query: str, filters: dict = None):
    # Combine vector search with metadata filtering
    search_expr = build_filter_expression(filters)
    
    results = collection.search(
        data=query_embedding,
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        expr=search_expr,  # Filter by metadata
        output_fields=["*"]
    )
    
    return results
```

### **Performance Optimization**

#### **Index Configuration**
```python
# IVF_FLAT index for balance of speed vs accuracy
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "IP",
    "params": {"nlist": 128}  # Adjust based on data size
}

# For larger datasets, consider:
# - IVF_PQ: Better compression, slight accuracy loss
# - HNSW: Better search speed, more memory usage
```

#### **Search Parameters**
```python
search_params = {
    "metric_type": "IP",
    "params": {
        "nprobe": 10,  # Number of clusters to search
        "max_empty_result_buckets": 2
    }
}
```

---

## 🔴 **Redis Architecture**

### **Data Structures**

#### **Session Storage**
```python
# Session key pattern: session:{session_id}
"session:sess_abc123" = {
    "user_id": "user_123",
    "created_at": "2024-01-01T10:00:00Z",
    "last_activity": "2024-01-01T10:15:00Z",
    "metadata": {...}
}
# TTL: 24 hours
```

#### **Conversation Cache**
```python  
# Recent conversation cache
"conv_cache:user_123" = {
    "recent_messages": [...],
    "context_summary": "User đang hỏi về thủ tục...",
    "last_topics": ["thường trú", "CCCD"]
}
# TTL: 2 hours
```

#### **Rate Limiting**
```python
# API rate limiting
"rate_limit:user_123:chat" = 50  # 50 requests
# TTL: 1 hour

"rate_limit:ip_192.168.1.100:api" = 1000  # 1000 requests  
# TTL: 1 hour
```

#### **Background Job Queue**
```python
# Celery job queue
"celery_queue:document_processing" = [
    {
        "task_id": "task_123",
        "function": "process_document",
        "args": ["document_id_456"],
        "status": "pending"
    }
]
```

### **Redis Configuration**
```python
# Connection settings
REDIS_URL = "redis://localhost:6379/0"
REDIS_DECODE_RESPONSES = True
REDIS_SOCKET_KEEPALIVE = True
REDIS_SOCKET_KEEPALIVE_OPTIONS = {}

# Memory policies
maxmemory_policy = "allkeys-lru"  # Evict least recently used keys
maxmemory = "1gb"
```

---

## 🔧 **Database Operations**

### **MongoDB Operations**

#### **Connection Management**
```python
# app/services/database.py
class MongoService:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        
    async def find_documents(self, collection: str, query: dict):
        return await self.db[collection].find(query).to_list(length=None)
        
    async def insert_document(self, collection: str, document: dict):
        return await self.db[collection].insert_one(document)
```

#### **Common Queries**
```python
# Find user conversations
conversations = await mongo.find_documents(
    "conversations",
    {"user_id": user_id, "created_at": {"$gte": date_from}}
)

# Search documents by keyword
documents = await mongo.find_documents(
    "documents", 
    {"keywords": {"$in": ["thường trú"]}, "processed": True}
)
```

### **Milvus Operations**

#### **Connection Management**
```python
# app/services/milvus_service.py
class MilvusService:
    def __init__(self):
        connections.connect(
            alias="default",
            host=MILVUS_HOST,
            port=MILVUS_PORT
        )
        self.collection = Collection("document_embeddings")
        self.collection.load()
        
    def search_documents(self, query_embedding, top_k=5):
        return self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=top_k
        )
```

### **Redis Operations**

#### **Cache Management**
```python
# app/services/cache_service.py
class CacheService:
    def __init__(self):
        self.redis = Redis.from_url(REDIS_URL)
        
    async def get_conversation_cache(self, user_id: str):
        key = f"conv_cache:{user_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
        
    async def set_session(self, session_id: str, data: dict, ttl: int = 86400):
        key = f"session:{session_id}"
        await self.redis.setex(key, ttl, json.dumps(data))
```

---

## 📊 **Database Monitoring**

### **Performance Metrics**

#### **MongoDB Monitoring**
```python
# Key metrics to track
- Connection pool usage
- Query execution time
- Index usage statistics
- Document growth rate
- Storage utilization
```

#### **Milvus Monitoring**
```python
# Vector DB metrics
- Search latency
- Index build time
- Memory usage
- Collection size
- Query throughput
```

#### **Redis Monitoring**
```python
# Cache metrics
- Hit/miss ratio
- Memory usage
- Key expiration rate
- Connection count
- Command statistics
```

### **Health Check Endpoints**
```python
# API health checks
@app.get("/health/databases")
async def check_database_health():
    return {
        "mongodb": await check_mongo_connection(),
        "milvus": await check_milvus_connection(), 
        "redis": await check_redis_connection()
    }
```

---

## 🔐 **Security Considerations**

### **MongoDB Security**
- Authentication enabled (username/password)
- TLS encryption for connections
- Role-based access control
- Regular backup schedule
- Index optimization

### **Milvus Security**  
- Network isolation
- Access control via API keys
- Data encryption at rest
- Regular index optimization
- Backup strategies

### **Redis Security**
- AUTH password protection
- Network binding restrictions
- SSL/TLS connections
- Key pattern restrictions
- Memory limit configuration

---

## 📈 **Scaling Strategies**

### **Vertical Scaling**
- Increase server resources (CPU, RAM, Storage)
- Optimize queries and indexes
- Tune database configurations

### **Horizontal Scaling**
- **MongoDB**: Replica sets và sharding
- **Milvus**: Distributed cluster mode
- **Redis**: Cluster mode và sharding

### **Performance Optimization**
- Query optimization và indexing
- Connection pooling
- Caching strategies
- Data archiving policies

---

*Database architecture designed for performance, scalability, and reliability in production environments.*
