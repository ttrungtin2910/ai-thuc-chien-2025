# 🌍 DVC.AI - Trợ lý dịch vụ công và cổng Kiến thức

Trợ lý AI thông minh cho dịch vụ công và hệ thống quản lý kiến thức, với thiết kế tone màu mệnh thổ ấm áp.

## 🚀 Tính năng chính

### Chức năng cơ bản
- ✅ **Đăng nhập** bảo mật với JWT authentication
- ✅ **Quản lý tài liệu** - Upload, xem, xóa file PDF và DOCX
- ✅ **Chatbot hỗ trợ** - Tương tác với trợ lý ảo
- ✅ **Upload đồng loạt** - Hỗ trợ nhiều file cùng lúc
- ✅ **WebSocket real-time** - Theo dõi tiến trình upload
- ✅ **Google Cloud Storage** - Lưu trữ file trên cloud
- ✅ **UI/UX chính phủ** - Thiết kế nghiêm túc, hiện đại

### Công nghệ sử dụng
- **Frontend:** ReactJS + Ant Design + MaisonNeue font
- **Backend:** Python FastAPI + Celery + Redis
- **Database:** In-memory (có thể mở rộng)
- **Storage:** Google Cloud Storage + Local uploads
- **Authentication:** JWT tokens
- **Real-time:** WebSocket + Socket.IO

## 📚 Hướng dẫn chi tiết

**📖 Xem hướng dẫn hoàn chỉnh tại:** [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md)

File này chứa tất cả thông tin chi tiết về:
- Cài đặt và cấu hình
- API documentation
- Theme design system
- Responsive design
- Troubleshooting
- Deployment
- Security considerations

## 🛠️ Quick Start

### 1. Clone repository
```bash
git clone [repository-url]
cd 02-AI-ThucChien
```

### 2. Start Backend
```bash
cd be
python dev.py start
```

### 3. Start Frontend
```bash
cd fe
npm install
npm start
```

### 4. Truy cập ứng dụng
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### Tài khoản mặc định
- **Username:** `admin`
- **Password:** `password123`

## 🎨 Theme Mệnh Thổ

Dự án sử dụng theme **Mệnh Thổ (Earth Element)** với:
- **Màu chính**: #D2691E (Cam đất chocolate)
- **Biểu tượng**: Trống đồng Đông Sơn
- **Font**: MaisonNeue (chính thức công ty)
- **Design**: Responsive, chuyên nghiệp, chính phủ

## 📁 Cấu trúc dự án

```
├── be/                     # Backend FastAPI
├── fe/                     # Frontend ReactJS
├── uploads/                # Global uploads
├── COMPLETE_GUIDE.md       # Hướng dẫn hoàn chỉnh
└── README.md               # File này
```

## 🚀 Deployment

Xem hướng dẫn chi tiết trong [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md) để biết:
- Production deployment
- Environment configuration
- Security setup
- Performance optimization

## 📞 Hỗ trợ

- **Documentation**: [`COMPLETE_GUIDE.md`](COMPLETE_GUIDE.md)
- **API Docs**: http://localhost:8001/docs
- **Email**: support@domain.gov.vn

## 📄 License

MIT License - Xem file LICENSE để biết chi tiết.

---

**Phiên bản:** 2.0.0  
**Cập nhật:** December 2024  
**Tác giả:** AI Assistant  
**Theme:** Mệnh Thổ (Earth Element)  
**Brand:** DVC.AI - Trợ lý dịch vụ công và cổng Kiến thức**
