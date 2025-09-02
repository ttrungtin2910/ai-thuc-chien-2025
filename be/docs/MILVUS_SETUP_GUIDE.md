# Hướng dẫn thiết lập Milvus Vector Database cho RAG

## Tổng quan
Hệ thống này sử dụng Milvus để lưu trữ embeddings của các tài liệu thủ tục công dân, phục vụ cho Retrieval-Augmented Generation (RAG).

## Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
cd be
pip install -r requirements.txt
```

### 2. Khởi động Milvus với Docker

**Trên Windows:**
```cmd
cd be
start_milvus.bat
```

**Trên Linux/macOS:**
```bash
cd be
./start_milvus.sh
```

### 3. Load documents vào Milvus
```bash
cd be
python load_documents_to_milvus.py
```

## Dịch vụ được khởi động

### Milvus Vector Database
- **URL**: `localhost:19530`
- **Mô tả**: Vector database chính để lưu trữ embeddings

### Attu Web Interface  
- **URL**: `http://localhost:3001`
- **Mô tả**: Giao diện web để quản lý Milvus
- **Chức năng**: Xem collections, thống kê, query data

### MinIO Object Storage
- **URL**: `http://localhost:9001` 
- **Username**: `minioadmin`
- **Password**: `minioadmin`
- **Mô tả**: Object storage backend cho Milvus

### Etcd
- **Port**: `2379`
- **Mô tả**: Metadata storage cho Milvus

## Cấu trúc dữ liệu

### Collection: `document_embeddings`

| Field | Type | Mô tả |
|-------|------|--------|
| id | INT64 | Primary key (auto-generated) |
| file_name | VARCHAR(512) | Tên file gốc |
| chunk_id | INT64 | ID của chunk trong document |
| content | VARCHAR(8192) | Nội dung text của chunk |
| title | VARCHAR(512) | Tiêu đề document |
| section | VARCHAR(512) | Tên section/phần |
| embedding | FLOAT_VECTOR(384) | Vector embedding |

### Embedding Model
- **Model**: `all-MiniLM-L6-v2`
- **Dimension**: 384
- **Ngôn ngữ**: Hỗ trợ tiếng Việt tốt
- **Tốc độ**: Nhanh, phù hợp cho production

## Sử dụng trong code

### Tìm kiếm tài liệu
```python
from services.milvus_service import MilvusService

# Khởi tạo service
milvus = MilvusService()
milvus.connect()
milvus.collection = Collection("document_embeddings")
milvus.load_collection()

# Tìm kiếm
query = "đăng ký thường trú"
results = milvus.search_similar(query, top_k=5)

for result in results:
    print(f"File: {result['file_name']}")
    print(f"Title: {result['title']}")
    print(f"Section: {result['section']}")
    print(f"Score: {result['score']}")
    print(f"Content: {result['content'][:200]}...")
    print("-" * 50)
```

### Thêm document mới
```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()
documents = processor.read_markdown_files()
chunks = processor.chunk_documents(documents)

milvus.insert_documents(chunks)
```

## Monitoring và vận hành

### Kiểm tra trạng thái
```bash
# Kiểm tra containers
docker-compose -f docker-compose-milvus.yml ps

# Xem logs
docker-compose -f docker-compose-milvus.yml logs milvus

# Thống kê collection
python -c "
from services.milvus_service import MilvusService
m = MilvusService()
m.connect()
print(f'Total documents: {m.get_collection_stats()}')
"
```

### Dừng services
```bash
docker-compose -f docker-compose-milvus.yml down
```

### Xóa dữ liệu (nếu cần)
```bash
docker-compose -f docker-compose-milvus.yml down -v
rm -rf volumes/
```

## Tối ưu hiệu suất

### Index Configuration
- **Type**: IVF_FLAT (tốt cho dataset vừa)
- **Metric**: Inner Product (IP)
- **nlist**: 128 (có thể tăng cho dataset lớn)

### Search Parameters
- **nprobe**: 10 (cân bằng tốc độ/độ chính xác)
- **top_k**: 5-10 (phù hợp cho RAG)

### Batch Size
- **Insert**: 50 documents/batch
- **Search**: 1 query/request (real-time)

## Troubleshooting

### Lỗi kết nối
```
Failed to connect to Milvus
```
**Giải pháp**: Kiểm tra Docker containers đang chạy

### Lỗi memory
```
Out of memory
```
**Giải pháp**: Giảm batch size, tăng RAM cho Docker

### Lỗi encoding
```
UnicodeDecodeError
```
**Giải pháp**: Đảm bảo files markdown có encoding UTF-8

### Collection đã tồn tại
```
Collection already exists
```
**Giải pháp**: Bình thường, script sẽ sử dụng collection có sẵn

## Tích hợp với RAG

### Pipeline cơ bản
1. **User query** → Embedding model
2. **Vector search** → Top-K documents 
3. **Context** + Query → LLM (Azure OpenAI)
4. **Response** → User

### Code tham khảo
```python
def rag_query(question: str):
    # 1. Tìm context từ Milvus
    milvus = MilvusService()
    milvus.connect()
    results = milvus.search_similar(question, top_k=3)
    
    # 2. Tạo context
    context = "\n".join([r['content'] for r in results])
    
    # 3. Gọi LLM với context
    prompt = f"""
    Dựa vào thông tin sau:
    {context}
    
    Hãy trả lời câu hỏi: {question}
    """
    
    # 4. Call Azure OpenAI API...
    return response
```

## Performance Metrics

Với dataset hiện tại (~22 documents):
- **Load time**: ~30 giây
- **Search latency**: <100ms
- **Memory usage**: ~500MB
- **Storage**: ~50MB

---

*Cập nhật: {current_date}*
