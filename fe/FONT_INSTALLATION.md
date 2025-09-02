# Hướng dẫn Cài đặt Font MaisonNeue

## Tổng quan

Dự án sử dụng font **MaisonNeue** làm font chính thức của công ty. Font này mang lại vẻ hiện đại, chuyên nghiệp và dễ đọc cho toàn bộ ứng dụng.

## Cách 1: Sử dụng Font Files (✅ ĐÃ CÀI ĐẶT)

### Bước 1: Font files đã có ✅
Font MaisonNeue đã được sao chép từ thư mục công ty:
`C:\Users\admin\OneDrive\10_VLU\09_Branding\02. Font\Font Maison Neue`

Các file font hiện có trong `fe/public/fonts/`:
   ```
   fe/public/fonts/
   ├── MaisonNeue-Thin.otf      (weight: 100)
   ├── MaisonNeue-Light.otf     (weight: 300)
   ├── MaisonNeue-Book.otf      (weight: 400)
   ├── MaisonNeue-Medium.otf    (weight: 500)
   ├── MaisonNeue-Demi.otf      (weight: 600)
   └── MaisonNeue-Bold.otf      (weight: 700)
   ```

### Bước 2: Font đã được cấu hình ✅
- File `fe/public/fonts.css` đã được cấu hình với format OpenType
- Font được import trong `fe/public/index.html`
- Font được áp dụng trong theme Ant Design và CSS

## Cách 2: Fallback Fonts

Nếu không có font MaisonNeue, ứng dụng sẽ tự động sử dụng các font fallback:

1. **Inter** (Google Fonts) - đã được import
2. **System fonts** khác

## Cách 3: Cài đặt từ Adobe Fonts (nếu có license)

Nếu công ty có license Adobe Fonts:

1. Thêm vào `fe/public/index.html`:
   ```html
   <link rel="stylesheet" href="https://use.typekit.net/[PROJECT_ID].css">
   ```

2. Cập nhật font-family trong CSS:
   ```css
   font-family: 'maison-neue', 'Inter', sans-serif;
   ```

## Font Weights được sử dụng (✅ ĐÃ CẤU HÌNH)

- **100 (Thin)**: Text rất nhẹ, decorative
- **300 (Light)**: Text phụ, captions  
- **400 (Book/Regular)**: Body text chính
- **500 (Medium)**: Labels, form controls
- **600 (Demi)**: Headings, buttons
- **700 (Bold)**: Titles, emphasis

**Lưu ý**: Tất cả font weights đã được cài đặt và cấu hình từ file gốc công ty.

## Kiểm tra Font

Để kiểm tra font đã load thành công:

1. Mở Developer Tools (F12)
2. Vào tab Network > Fonts
3. Reload trang và xem các font files được tải
4. Hoặc inspect element và check computed styles

## Lưu ý ⚠️

- ✅ **Font files đã được cài đặt** từ thư mục chính thức công ty
- ✅ **Font files được commit** vào git vì đây là font chính thức công ty
- 🔄 **Fallback fonts**: Font Inter vẫn được sử dụng làm backup
- 📁 **Nguồn gốc**: Font được sao chép từ `C:\Users\admin\OneDrive\10_VLU\09_Branding\02. Font\Font Maison Neue`

## Trạng thái hiện tại

- ✅ Font MaisonNeue đã được cài đặt hoàn toàn
- ✅ 6 font weights từ Thin (100) đến Bold (700)
- ✅ Format OpenType (.otf) được hỗ trợ đầy đủ
- ✅ CSS configuration đã hoàn thành
- ✅ Theme integration đã sẵn sàng

## Liên hệ

Nếu gặp vấn đề với font, liên hệ:
- Bộ phận IT: it@company.com
- Designer: design@company.com
