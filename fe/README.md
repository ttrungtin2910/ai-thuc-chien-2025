# Document Management Frontend

ReactJS frontend cho hệ thống quản lý tài liệu với thiết kế phong cách chính phủ.

## Tính năng

- 🔐 **Xác thực người dùng** với JWT
- 📁 **Quản lý tài liệu** (upload, xem, xóa)
- 🤖 **Chatbot hỗ trợ** trực tuyến
- 🎨 **Giao diện chính phủ** nghiêm túc, hiện đại
- 📱 **Responsive design** tương thích mobile

## Công nghệ sử dụng

- **React 18** - Frontend framework
- **Ant Design** - UI component library
- **React Router** - Navigation
- **Axios** - HTTP client
- **Styled Components** - CSS-in-JS
- **Moment.js** - Date formatting

## Cài đặt

### 1. Cài đặt dependencies

```bash
cd fe
npm install
```

### 2. Cấu hình môi trường

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=Hệ thống Quản lý Tài liệu
```

### 3. Chạy ứng dụng

```bash
# Development mode
npm start

# Build for production
npm run build

# Run tests
npm test
```

Ứng dụng sẽ chạy tại: http://localhost:3000

## Cấu trúc dự án

```
fe/
├── public/
│   └── index.html
├── src/
│   ├── components/          # React components
│   │   ├── DocumentManagement.js
│   │   └── ChatBot.js
│   ├── contexts/           # React contexts
│   │   └── AuthContext.js
│   ├── pages/              # Page components
│   │   ├── LoginPage.js
│   │   └── MainPage.js
│   ├── services/           # API services
│   │   └── api.js
│   ├── App.js
│   ├── index.js
│   ├── index.css
│   └── App.css
├── package.json
└── README.md
```

## Tài khoản mặc định

- **Username:** `admin`
- **Password:** `password123`

## API Integration

Frontend kết nối với FastAPI backend thông qua các endpoint:

- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Thông tin user
- `GET /api/documents` - Danh sách tài liệu
- `POST /api/documents/upload` - Upload tài liệu
- `DELETE /api/documents/{id}` - Xóa tài liệu
- `POST /api/chatbot/message` - Chat với bot

## Tính năng chính

### 1. Quản lý Tài liệu
- Upload file PDF và DOCX
- Hiển thị danh sách tài liệu
- Thống kê file theo loại
- Xóa tài liệu
- Drag & drop upload

### 2. Chatbot
- Giao diện chat real-time
- Câu hỏi thường gặp
- Hỗ trợ trực tuyến

### 3. Thiết kế Chính phủ
- Màu sắc nghiêm túc: #1f4e79 (xanh dương đậm)
- Typography rõ ràng, dễ đọc
- Layout responsive
- Accessibility tốt

## Scripts có sẵn

```bash
# Chạy development server
npm start

# Build production
npm run build

# Chạy tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## Deployment

### Build for production

```bash
npm run build
```

### Deploy với Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /path/to/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Browser Support

- Chrome >= 60
- Firefox >= 60
- Safari >= 12
- Edge >= 79

## Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.
