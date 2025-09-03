# 🗄️ Cấu trúc Vector Database - Milvus

## 📊 Schema của Collection "document_embeddings"

### Các trường dữ liệu:

| Field | Type | Max Length | Description | Example |
|-------|------|------------|-------------|---------|
| **id** | INT64 | - | Primary Key (Auto-generated) | 1, 2, 3, ... |
| **file_name** | VARCHAR | 512 | Tên file markdown gốc | `doc_congdan_1.000466.md` |
| **chunk_id** | INT64 | - | ID chunk duy nhất | `0-99` (Section 1), `100-199` (Section 2) |
| **content** | VARCHAR | 8192 | Nội dung text chunk | `"Thủ tục đăng ký thường trú..."` |
| **title** | VARCHAR | 512 | Tiêu đề document từ `# header` | `"Thủ tục hành chính công dân"` |
| **section** | VARCHAR | 512 | Tiêu đề section từ `## header` | `"Đăng ký thường trú"` |
| **embedding** | FLOAT_VECTOR | 3072 | Vector embedding từ OpenAI | `[0.123, -0.456, ...]` |

## 🔧 Cấu hình Vector

- **Model**: OpenAI `text-embedding-3-large`
- **Dimension**: 3072 (cao nhất của OpenAI)
- **Metric**: Inner Product (IP)
- **Index**: IVF_FLAT với nlist=128

## 📖 Quy trình xử lý Document

### 1. **Document Reading**
```python
# Đọc file markdown từ ../data/thutuccongdan/
documents = document_processor.read_markdown_files()
```

### 2. **Content Parsing**
```markdown
# Tiêu đề chính (title)
Nội dung mở đầu...

## Section 1 (section)
Nội dung section 1...

## Section 2 (section)
Nội dung section 2...
```

### 3. **Chunking Strategy**

#### **Section Chunks** (chunk_id: 0-9999)
- Mỗi section được chia thành chunks riêng biệt
- **chunk_id pattern**: `section_index * 100 + chunk_index`
  - Section 0: chunk_id 0, 1, 2, ...
  - Section 1: chunk_id 100, 101, 102, ...
  - Section 2: chunk_id 200, 201, 202, ...

#### **Full Document Chunks** (chunk_id: 9000+)
- Toàn bộ document được chia thành chunks
- **chunk_id pattern**: `9000 + chunk_index`
- **section**: "Full Document"

### 4. **Chunk Parameters**
```python
chunk_size = 1000        # Max 1000 characters per chunk
chunk_overlap = 200      # 200 characters overlap between chunks
```

### 5. **Text Splitting Logic**
- Ưu tiên break tại sentence endings (`.`, `!`, `?`)
- Tìm trong 100 characters cuối của chunk
- Overlap 200 characters để giữ context

## 🔍 Example Data Structure

### Input Document:
```markdown
# Thủ tục căn cước công dân

## Điều kiện làm căn cước
Công dân từ đủ 14 tuổi trở lên...

## Hồ sơ cần thiết
1. Đơn đề nghị cấp căn cước...
2. Giấy khai sinh...
```

### Output Chunks in Milvus:

| id | file_name | chunk_id | title | section | content | embedding |
|----|-----------|----------|-------|---------|---------|-----------|
| 1 | `doc_congdan_1.md` | 0 | `"Thủ tục căn cước công dân"` | `"Điều kiện làm căn cước"` | `"Công dân từ đủ 14 tuổi..."` | `[0.123, -0.456, ...]` |
| 2 | `doc_congdan_1.md` | 100 | `"Thủ tục căn cước công dân"` | `"Hồ sơ cần thiết"` | `"1. Đơn đề nghị cấp..."` | `[0.789, 0.012, ...]` |
| 3 | `doc_congdan_1.md` | 9000 | `"Thủ tục căn cước công dân"` | `"Full Document"` | `"# Thủ tục căn cước..."` | `[0.345, -0.678, ...]` |

## 🔍 Search Process

### 1. **Query Processing**
```python
query = "Làm căn cước công dân cần giấy tờ gì?"
query_embedding = openai_service.get_embedding(query)  # Vector 3072 dim
```

### 2. **Vector Search**
```python
results = milvus_service.search_similar(
    query_embedding, 
    top_k=5,
    metric_type="IP"  # Inner Product similarity
)
```

### 3. **Result Ranking**
- Sắp xếp theo similarity score (càng cao càng relevant)
- Trả về top-k documents có score cao nhất
- Include metadata: title, section, file_name

## 📈 Performance Characteristics

### **Storage Efficiency**
- **Text**: VARCHAR với length limits hợp lý
- **Vectors**: Float32 optimized for fast search
- **Indexing**: IVF_FLAT for balance between speed vs accuracy

### **Search Performance**
- **Latency**: ~10-50ms cho typical queries
- **Throughput**: Hàng nghìn queries/second
- **Accuracy**: High precision với text-embedding-3-large

### **Scalability**
- **Documents**: Có thể scale đến millions documents
- **Vector dimension**: 3072 optimal cho Vietnamese text
- **Concurrent users**: Support multiple simultaneous searches

## 🛠️ Maintenance Operations

### **Loading Documents**
```bash
cd be
python scripts/load_documents_to_milvus.py
```

### **Collection Statistics**
```python
stats = milvus_service.get_collection_stats()
print(f"Total entities: {stats}")
```

### **Search Testing**
```python
results = milvus_service.search_similar("test query", top_k=3)
for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"Content: {result['content'][:100]}...")
```

## 💡 Best Practices

### **Document Organization**
- ✅ Sử dụng clear section headers (`## header`)
- ✅ Giữ content structured và có logic
- ✅ Avoid quá dài trong một section

### **Chunking Strategy**
- ✅ Chunk size 1000 characters optimal cho Vietnamese
- ✅ Overlap 200 characters preserves context
- ✅ Both section và full document chunks for comprehensive search

### **Search Optimization**
- ✅ Use specific keywords trong queries
- ✅ Include context trong search queries
- ✅ Combine multiple search results for better answers

---

**Vector DB**: Milvus 2.3.3  
**Embedding Model**: OpenAI text-embedding-3-large (3072 dim)  
**Collection**: document_embeddings  
**Index**: IVF_FLAT with Inner Product similarity
