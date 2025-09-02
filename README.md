# DVC.AI - Trợ lý dịch vụ công và cổng Kiến thức

Trợ lý AI thông minh cho dịch vụ công và hệ thống quản lý kiến thức, với thiết kế tone màu mệnh thổ ấm áp.

## 🚀 Tính năng chính

### Chức năng cơ bản
- ✅ **Đăng nhập** bảo mật với JWT authentication
- ✅ **Quản lý tài liệu** - Upload, xem, xóa file PDF và DOCX
- ✅ **Chatbot hỗ trợ** - Tương tác với trợ lý ảo
- ✅ **UI/UX chính phủ** - Thiết kế nghiêm túc, hiện đại

### Công nghệ sử dụng
- **Frontend:** ReactJS + Ant Design
- **Backend:** Python FastAPI
- **Database:** In-memory (có thể mở rộng)
- **Authentication:** JWT tokens
- **File Upload:** Multipart form data

## 📁 Cấu trúc dự án

```
d:\02-VLU\02-AI-ThucChien\
├── be/                     # Backend FastAPI
│   ├── main.py            # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   ├── environment.yml    # Conda environment
│   ├── uploads/           # Thư mục lưu file upload
│   └── README.md
├── fe/                     # Frontend ReactJS
│   ├── public/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── ...
│   ├── package.json
│   └── README.md
└── README.md              # File này
```

## 🛠️ Cài đặt và Chạy

### Bước 1: Setup Backend (FastAPI)

```bash
# Di chuyển vào thư mục backend
cd be

# Tạo môi trường Conda (khuyến nghị)
conda env create -f environment.yml
conda activate document-management-be

# Hoặc sử dụng pip
pip install -r requirements.txt

# Chạy backend server
python main.py
```

Backend sẽ chạy tại: **http://localhost:8000**

### Bước 2: Setup Frontend (ReactJS)

```bash
# Mở terminal mới, di chuyển vào thư mục frontend
cd fe

# Cài đặt dependencies
npm install

# Chạy frontend development server
npm start
```

Frontend sẽ chạy tại: **http://localhost:3000**

### Bước 3: Truy cập ứng dụng

1. Mở trình duyệt và truy cập: http://localhost:3000
2. Đăng nhập với tài khoản:
   - **Username:** `admin`
   - **Password:** `password123`

## 🎨 Thiết kế UI/UX

### Phong cách Mệnh Thổ (Earth Element)
- **Màu chủ đạo:** #D2691E (Cam đất chocolate)
- **Màu accent:** #CD853F (Vàng đất sandy brown)
- **Màu phụ:** #FDF5E6 (Be kem old lace)
- **Font:** MaisonNeue (✅ đã cài đặt từ thư mục công ty) với fallback Inter
- **Biểu tượng:** Trống đồng Đông Sơn - biểu tượng văn hóa Việt Nam
- **Layout:** Sạch sẽ, rõ ràng, mang đậm bản sắc dân tộc

### Responsive Design
- Tương thích desktop, tablet, mobile
- Breakpoints: 768px, 1024px, 1200px
- Touch-friendly trên mobile

## 📋 API Documentation

Sau khi chạy backend, truy cập Swagger UI tại: http://localhost:8000/docs

### Các endpoint chính:

#### Authentication
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Lấy thông tin user

#### Document Management
- `GET /api/documents` - Lấy danh sách tài liệu
- `POST /api/documents/upload` - Upload tài liệu
- `DELETE /api/documents/{id}` - Xóa tài liệu

#### Chatbot
- `POST /api/chatbot/message` - Gửi tin nhắn đến chatbot

## 📱 Screenshots

### Màn hình Đăng nhập
- Logo và branding chính phủ
- Form đăng nhập đơn giản, bảo mật
- Responsive design

### Màn hình Chính
- Header với thông tin user
- Tab navigation: Quản lý Tài liệu / Hỗ trợ Trực tuyến
- Statistics dashboard

### Quản lý Tài liệu
- Upload area với drag & drop
- Danh sách tài liệu với filtering
- File type icons và metadata

### Chatbot
- Giao diện chat real-time
- Quick questions
- Typing indicators

## 🚀 Deployment

### Backend Deployment
```bash
# Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Using Docker (tùy chọn)
docker build -t document-backend .
docker run -p 8000:8000 document-backend
```

### Frontend Deployment
```bash
# Build production
npm run build

# Serve with nginx/apache
# Copy build/ folder to web server
```

## 🔧 Cấu hình nâng cao

### Environment Variables (Backend)
- `SECRET_KEY`: JWT secret key
- `UPLOAD_DIR`: Thư mục lưu file upload
- `MAX_FILE_SIZE`: Kích thước file tối đa

### Environment Variables (Frontend)
- `REACT_APP_API_URL`: URL của backend API
- `REACT_APP_APP_NAME`: Tên ứng dụng

## 📝 Tính năng sẽ phát triển

- [ ] **Database integration** (PostgreSQL/MongoDB)
- [ ] **File preview** cho PDF và DOCX
- [ ] **Advanced search** và filtering
- [ ] **User management** và phân quyền
- [ ] **Document versioning**
- [ ] **Email notifications**
- [ ] **Advanced chatbot** với AI/NLP
- [ ] **Audit logs** và reporting
- [ ] **Multi-language support**

## 🐛 Troubleshooting

### Backend không start được
```bash
# Kiểm tra Python version
python --version  # Cần >= 3.8

# Kiểm tra dependencies
pip list

# Kiểm tra port 8000
netstat -an | grep 8000
```

### Frontend không kết nối được backend
```bash
# Kiểm tra backend đang chạy
curl http://localhost:8000

# Kiểm tra CORS configuration
# Xem console browser để debug
```

### File upload lỗi
- Kiểm tra file format (chỉ PDF, DOCX)
- Kiểm tra file size (< 10MB)
- Kiểm tra quyền write vào thư mục uploads/

## 📞 Hỗ trợ

- **Email:** support@domain.gov.vn
- **Hotline:** 1900-xxxx
- **Documentation:** http://localhost:8000/docs

## 📄 License

MIT License - Xem file LICENSE để biết chi tiết.

---

**Phiên bản:** 1.0.0  
**Cập nhật:** December 2024  
**Tác giả:** AI Assistant
