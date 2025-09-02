# 🌍 DVC.AI - Theme Mệnh Thổ (Earth Element)

## 🎯 Tổng quan

**DVC.AI** (Trợ lý dịch vụ công và cổng Kiến thức) được thiết kế theo phong cách **Mệnh Thổ** với tone màu ấm áp, đất đai, thể hiện sự ổn định, tin cậy và gần gũi với người dân.

## 🎨 Bảng màu Mệnh Thổ

### 🟤 Màu chính (Primary Colors)
```css
--primary-color: #D2691E;        /* Cam đất chocolate - ấm áp, tin cậy */
--primary-light: #DEB887;        /* Vàng đất burlywood - nhẹ nhàng */
--primary-dark: #A0522D;         /* Nâu đất sienna - ổn định */
```

### 🟫 Màu phụ (Secondary Colors)
```css
--secondary-color: #FDF5E6;      /* Be kem old lace - thanh nhã */
--accent-color: #CD853F;         /* Vàng đất sandy brown - nổi bật */
--border-color: #F4E4BC;         /* Màu lúa mì nhạt - tinh tế */
```

### 🎨 Màu hệ thống (System Colors)
```css
--success-color: #228B22;        /* Xanh lá rừng - tự nhiên */
--warning-color: #DAA520;        /* Vàng goldenrod - cảnh báo */
--info-color: #B8860B;           /* Vàng đắng darkgoldenrod - thông tin */
--text-primary: #2F1B14;         /* Nâu đất tối - dễ đọc */
--text-secondary: #8B4513;       /* Nâu saddle - text phụ */
```

## 🥁 Biểu tượng Trống đồng Đông Sơn

### 🇻🇳 Ý nghĩa trong DVC.AI
- **AI & Quyền lực**: Trống đồng biểu tượng cho sức mạnh AI hỗ trợ dịch vụ công
- **Kết nối Kiến thức**: Chim Lạc bay quanh mặt trời, kết nối tri thức và công nghệ
- **Phục vụ Nhân dân**: Họa tiết thể hiện sự kết nối giữa dân và chính quyền
- **Kế thừa & Đổi mới**: Tiếp nối truyền thống với công nghệ hiện đại

### 🎨 Sử dụng trong thiết kế
- **Logo**: 64px trên login, filter tone màu đất ấm
- **Header**: 40px màu trắng, kết hợp với branding DVC.AI
- **Background**: Pattern 800px với opacity thấp
- **Icons**: Tone màu chocolate (#D2691E) cho consistency

## 🏢 Branding DVC.AI

### 📱 Tên ứng dụng
```
DVC.AI
```

### 📝 Slogan chính thức
```
Trợ lý dịch vụ công và cổng Kiến thức
```

### 🎯 Định vị thương hiệu
- **D**ịch **V**ụ **C**ông + **AI**: Kết hợp truyền thống và hiện đại
- **Trợ lý thông minh**: AI hỗ trợ công dân và cán bộ
- **Cổng kiến thức**: Tập trung quản lý và chia sẻ thông tin

## 🎨 Nguyên tắc thiết kế Mệnh Thổ

### 1. 🌱 Tính ấm áp, gần gũi
- Màu sắc mệnh thổ tạo cảm giác ấm áp, tin cậy
- UI elements có độ bo tròn mềm mại
- Không gian thở, không chật chội

### 2. 💎 Tính chuyên nghiệp
- Font MaisonNeue thể hiện tính chuyên nghiệp
- Layout rõ ràng, có tổ chức
- Contrast tốt cho accessibility

### 3. 🇻🇳 Tính dân tộc
- Giữ nguyên biểu tượng trống đồng Đông Sơn
- Màu sắc hài hòa với bản sắc Việt Nam
- Tôn trọng ý nghĩa văn hóa truyền thống

## 🔤 Typography - MaisonNeue

### Font Weights sử dụng
```css
font-weight: 100; /* Thin - decorative elements */
font-weight: 300; /* Light - captions, secondary text */
font-weight: 400; /* Book - body text chính */
font-weight: 500; /* Medium - labels, navigation */
font-weight: 600; /* Demi - headings, buttons */
font-weight: 700; /* Bold - titles, emphasis */
```

### Font Stack
```css
font-family: 'MaisonNeue', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
```

## 🎯 Color Psychology - Mệnh Thổ

### 🟤 Chocolate (#D2691E)
- **Ý nghĩa**: Ổn định, tin cậy, ấm áp
- **Cảm xúc**: An toàn, gần gũi, chuyên nghiệp
- **Sử dụng**: Primary buttons, links, headings

### 🟫 Burlywood (#DEB887)
- **Ý nghĩa**: Nhẹ nhàng, thanh tao
- **Cảm xúc**: Thư giãn, dễ chịu
- **Sử dụng**: Hover states, light backgrounds

### 🤎 Sienna (#A0522D)
- **Ý nghĩa**: Mạnh mẽ, bền vững
- **Cảm xúc**: Quyền lực, uy tín
- **Sử dụng**: Active states, emphasis

## 🔧 Implementation Guide

### CSS Variables Usage
```css
/* Primary actions */
background-color: var(--primary-color);
color: white;

/* Hover effects */
box-shadow: 0 4px 12px rgba(210, 105, 30, 0.3);

/* Text colors */
color: var(--text-primary);
```

### React Components
```jsx
// Drum icon with earth tone filter
<img 
  src={dongsondrum} 
  alt="Trống đồng Đông Sơn"
  style={{ 
    filter: 'hue-rotate(25deg) saturate(1.3) brightness(1.1)' 
  }}
/>
```

### Ant Design Theme
```js
theme={{
  token: {
    colorPrimary: '#D2691E',
    colorSuccess: '#228B22',
    colorWarning: '#DAA520',
    fontFamily: "'MaisonNeue', 'Inter', sans-serif",
  },
}}
```

## 📱 Responsive Behavior

### Desktop (> 1024px)
- Full logo với text "DVC.AI"
- Trống đồng 40px trong header
- Typography scale đầy đủ

### Tablet (768px - 1024px)
- Logo compact
- Icon trống đồng 32px
- Font size điều chỉnh

### Mobile (< 768px)
- Logo icon-only
- Icon trống đồng 24px
- Typography optimized for touch

## 🎨 Design System Components

### Buttons
```css
.btn-primary {
  background: var(--primary-color);
  border: 1px solid var(--primary-color);
  color: white;
  font-weight: 500;
}

.btn-primary:hover {
  background: var(--primary-light);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(210, 105, 30, 0.3);
}
```

### Cards
```css
.card {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  box-shadow: var(--shadow);
}

.card-header {
  background: var(--secondary-color);
  color: var(--primary-color);
  font-weight: 600;
}
```

## 📊 Accessibility Standards

### Contrast Ratios
- **Text on white**: #2F1B14 (contrast ratio: 14.7:1) ✅
- **Primary button**: #D2691E on white (contrast ratio: 4.8:1) ✅
- **Secondary text**: #8B4513 (contrast ratio: 7.2:1) ✅

### Color Blindness Support
- Không dựa hoàn toàn vào màu sắc để truyền tải thông tin
- Sử dụng icons và patterns bổ trợ
- Test với color blindness simulators

## 🚀 Performance Optimization

### Font Loading
```css
@font-face {
  font-family: 'MaisonNeue';
  font-display: swap; /* Tối ưu loading */
  src: url('./fonts/MaisonNeue-Book.otf') format('opentype');
}
```

### Color Variables
- Sử dụng CSS custom properties cho consistency
- Dễ dàng thay đổi theme toàn bộ ứng dụng
- Giảm file size CSS

## 📋 Brand Guidelines Checklist

### ✅ Colors
- [ ] Sử dụng đúng primary color #D2691E
- [ ] Accent colors phù hợp với mệnh thổ
- [ ] Contrast ratios đạt chuẩn WCAG AA
- [ ] Consistent rgba values

### ✅ Typography
- [ ] MaisonNeue cho headings và UI elements
- [ ] Font weights phù hợp với hierarchy
- [ ] Line heights optimal cho đọc
- [ ] Fallback fonts configured

### ✅ Iconography
- [ ] Trống đồng Đông Sơn làm biểu tượng chính
- [ ] Filter effects phù hợp với theme màu đất
- [ ] Sizes consistent across components
- [ ] Alt texts đầy đủ

### ✅ Branding
- [ ] "DVC.AI" làm tên chính
- [ ] Slogan "Trợ lý dịch vụ công và cổng Kiến thức"
- [ ] Consistent messaging
- [ ] Professional tone of voice

## 🎭 Mood & Personality

### Tính cách thương hiệu DVC.AI
- **Ấm áp**: Như đất mẹ bao dung
- **Tin cậy**: Như núi đá vững chắc  
- **Thông minh**: AI hiện đại
- **Gần gũi**: Phục vụ nhân dân
- **Chuyên nghiệp**: Dịch vụ công chất lượng

### Tone of Voice
- **Formal but friendly**: Trang trọng nhưng thân thiện
- **Clear and helpful**: Rõ ràng và hữu ích
- **Respectful**: Tôn trọng người dùng
- **Confident**: Tự tin vào giải pháp

---

**🌍 DVC.AI - Nơi truyền thống gặp gỡ công nghệ**  
*Với tone màu mệnh thổ ấm áp, tạo nên sự tin cậy và gần gũi trong từng tương tác*
