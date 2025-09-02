# Document Management Backend

FastAPI backend cho hệ thống quản lý tài liệu.

## Cài đặt

### Sử dụng Conda (Khuyến nghị)

```bash
# Tạo môi trường conda
conda env create -f environment.yml

# Kích hoạt môi trường
conda activate document-management-be
```

### Sử dụng pip

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
# Chạy development server
python main.py

# Hoặc sử dụng uvicorn trực tiếp
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server sẽ chạy tại: http://localhost:8000

## API Documentation

Sau khi chạy server, truy cập:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tài khoản mặc định

- Username: `admin`
- Password: `password123`

## Cấu trúc API

- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Lấy thông tin user hiện tại
- `POST /api/documents/upload` - Upload tài liệu
- `GET /api/documents` - Lấy danh sách tài liệu
- `DELETE /api/documents/{id}` - Xóa tài liệu
- `POST /api/chatbot/message` - Gửi tin nhắn tới chatbot

## Lưu ý

- File upload được lưu trong thư mục `uploads/`
- Chỉ hỗ trợ file PDF và DOCX
- Token JWT có thời hạn 24 giờ
