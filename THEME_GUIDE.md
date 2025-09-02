# Hướng dẫn Theme Mệnh Thổ (Earth Element)

## 🌍 Tổng quan

**DVC.AI** được thiết kế theo phong cách **Mệnh Thổ (Earth Element)** với tone màu ấm áp, đất đai, thể hiện sự ổn định, tin cậy và gần gũi. Biểu tượng **Trống đồng Đông Sơn** vẫn được giữ lại để thể hiện bản sắc văn hóa Việt Nam.

## 🎨 Bảng màu Mệnh Thổ

### Màu chính
```css
--primary-color: #D2691E;        /* Cam đất chocolate */
--primary-light: #DEB887;        /* Vàng đất burlywood */
--primary-dark: #A0522D;         /* Nâu đất sienna */
```

### Màu phụ
```css
--secondary-color: #FDF5E6;      /* Be kem old lace */
--accent-color: #CD853F;         /* Vàng đất sandy brown */
--border-color: #F4E4BC;         /* Màu lúa mì nhạt */
```

### Màu hệ thống
```css
--success-color: #28a745;        /* Xanh lá thành công */
--warning-color: #ffc107;        /* Vàng cảnh báo */
--info-color: #17a2b8;          /* Xanh thông tin */
--text-primary: #212529;         /* Text chính */
--text-secondary: #6c757d;       /* Text phụ */
```

## 🥁 Biểu tượng Trống đồng Đông Sơn

### Ý nghĩa văn hóa và DVC.AI
- **Biểu tượng quyền lực**: Thể hiện sức mạnh AI hỗ trợ dịch vụ công
- **Kết nối trời đất**: Chim Lạc bay quanh mặt trời, kết nối kiến thức và công nghệ
- **Đời sống xã hội**: Họa tiết thể hiện sự kết nối giữa dân và chính quyền
- **Nghệ thuật đỉnh cao**: Tiếp nối truyền thống với công nghệ hiện đại

### Các yếu tố thiết kế
1. **Mặt trời trung tâm**: Ngôi sao 14 cánh
2. **Chim Lạc**: 5 con chim bay quanh mặt trời
3. **Thuyền và đời sống**: Họa tiết sinh hoạt xã hội
4. **Vòng tròn đồng tâm**: Biểu tượng chu kỳ thời gian

### Sử dụng trong ứng dụng
- **Logo chính**: Icon 64x64px trên màn hình login
- **Header**: Icon 40x40px màu trắng
- **Background**: Hình nền lớn 800x800px với opacity thấp
- **Filter effects**: Thay đổi màu sắc phù hợp với theme

## 🔤 Typography

### Font chính: MaisonNeue
- **Light (300)**: Caption, text phụ
- **Regular (400)**: Body text
- **Medium (500)**: Labels, form controls
- **Demi (600)**: Headings, buttons  
- **Bold (700)**: Titles, emphasis

### Font fallback: Inter
- Sử dụng từ Google Fonts khi không có MaisonNeue
- Style tương tự, đảm bảo tính nhất quán

## 🎯 Nguyên tắc thiết kế

### 1. Tính dân tộc
- Sử dụng biểu tượng trống đồng một cách tôn trọng
- Màu sắc phù hợp với tinh thần dịch vụ công
- Không làm mất đi ý nghĩa văn hóa

### 2. Tính chuyên nghiệp
- Giao diện sạch sẽ, rõ ràng
- Màu sắc hài hòa, dễ đọc
- Accessibility tốt cho mọi người dùng

### 3. Tính hiện đại
- Responsive design
- Smooth animations
- Clean typography
- Intuitive UX

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

### Quy tắc responsive
- Logo thu nhỏ trên mobile
- Text size điều chỉnh theo màn hình
- Spacing tối ưu cho touch interface

## 🔧 Cách sử dụng

### CSS Variables
```css
/* Sử dụng màu chính */
background-color: var(--primary-color);

/* Sử dụng shadow với màu primary */
box-shadow: 0 4px 12px rgba(0, 115, 230, 0.3);
```

### React Components
```jsx
// Import icon trống đồng
import dongsondrum from '../assets/dongson-drum.svg';

// Sử dụng với filter để thay đổi màu
<img 
  src={dongsondrum} 
  alt="Trống đồng Đông Sơn"
  style={{ 
    width: '40px', 
    height: '40px', 
    filter: 'brightness(0) invert(1)' // Màu trắng
  }}
/>
```

### Ant Design Theme
```js
theme={{
  token: {
    colorPrimary: '#0073e6',
    colorError: '#d32f2f',
    fontFamily: "'MaisonNeue', 'Inter', sans-serif",
  },
}}
```

## 🎨 Color Palette Visual

### Primary Colors
- 🔵 `#0073e6` - Primary Blue
- 🔷 `#3399ff` - Light Blue  
- 🔹 `#0056b3` - Dark Blue

### Accent Colors
- 🔴 `#d32f2f` - National Red
- ⚪ `#f0f8ff` - Light Background
- 🔘 `#cce7ff` - Border Blue

## 📋 Checklist thiết kế

### ✅ Màu sắc
- [ ] Sử dụng đúng primary color #0073e6
- [ ] Accent color #d32f2f cho các element quan trọng
- [ ] Contrast ratio đạt chuẩn WCAG AA
- [ ] Consistent across all components

### ✅ Typography  
- [ ] MaisonNeue làm font chính
- [ ] Inter làm fallback font
- [ ] Font weights phù hợp với hierarchy
- [ ] Line height tối ưu cho đọc

### ✅ Iconography
- [ ] Trống đồng Đông Sơn làm logo chính
- [ ] Size phù hợp với context
- [ ] Filter effects đúng màu theme
- [ ] Alt text đầy đủ cho accessibility

### ✅ Layout
- [ ] Consistent spacing system
- [ ] Proper responsive behavior  
- [ ] Background pattern không che lấp content
- [ ] Navigation intuitive và clear

## 🚀 Performance

### Tối ưu hóa
- SVG icon nhẹ và scalable
- CSS variables cho consistent theming
- Minimal color palette
- Efficient responsive design

### Loading
- Font preload cho performance
- SVG inline để tránh HTTP requests
- Background lazy loading

## 📞 Liên hệ

Nếu có thắc mắc về thiết kế hoặc cần hỗ trợ implement:
- **Design System**: design@company.com
- **Frontend Team**: frontend@company.com  
- **Cultural Advisor**: culture@company.com

---

*"Trống đồng Đông Sơn - Biểu tượng văn hóa thiêng liêng của dân tộc Việt"*
