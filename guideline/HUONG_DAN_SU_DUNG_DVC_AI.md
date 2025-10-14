# 📘 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG DVC.AI
## Trợ lý ảo thông minh về dịch vụ công và thủ tục hành chính Việt Nam

---

## 📋 Mục lục

1. [Giới thiệu](#giới-thiệu)
2. [Đăng nhập hệ thống](#đăng-nhập-hệ-thống)
3. [Giao diện chính](#giao-diện-chính)
4. [Hỗ trợ trực tuyến (Chatbot AI)](#hỗ-trợ-trực-tuyến)
5. [Kho tri thức (Vector Database)](#kho-tri-thức)
6. [Quản lý tài liệu](#quản-lý-tài-liệu)
7. [Tải lên tài liệu](#tải-lên-tài-liệu)
8. [Câu hỏi thường gặp](#câu-hỏi-thường-gặp)

---

## 🎯 Giới thiệu

**DVC.AI** là hệ thống trợ lý ảo thông minh được phát triển bằng công nghệ AI tiên tiến, giúp người dân tra cứu và tìm hiểu thông tin về các thủ tục hành chính, dịch vụ công một cách nhanh chóng và chính xác.

### ✨ Tính năng nổi bật

- 🤖 **Trợ lý AI thông minh**: Trả lời câu hỏi tự nhiên, thân thiện và chính xác
- 📚 **Kho tri thức phong phú**: Tìm kiếm semantic với công nghệ Vector Database
- 📄 **Quản lý tài liệu**: Upload và quản lý tài liệu đa dạng (PDF, Word, TXT, Image)
- ⚡ **Xử lý thời gian thực**: Theo dõi tiến trình upload và xử lý file ngay lập tức
- 🔍 **Tìm kiếm thông minh**: Tìm kiếm theo ngữ nghĩa, không chỉ từ khóa
- 💬 **Trò chuyện tự nhiên**: Giao tiếp với AI như nói chuyện với người thật

### 🔧 Công nghệ sử dụng

- **AI Models**: GPT-4o, Text-Embedding-3-Large (OpenAI)
- **Vector Database**: Milvus (tìm kiếm semantic)
- **RAG Technology**: Retrieval-Augmented Generation
- **Real-time**: WebSocket cho cập nhật trực tiếp
- **Backend**: FastAPI, LangGraph, Celery
- **Frontend**: React.js, Ant Design

---

## 🔐 Đăng nhập hệ thống

### Bước 1: Truy cập trang đăng nhập

Truy cập hệ thống qua địa chỉ: `dvc.ink`

**[Chỗ dán ảnh: Màn hình đăng nhập]**

### Bước 2: Nhập thông tin đăng nhập

- **Tên đăng nhập**: Nhập username được cấp
- **Mật khẩu**: Nhập mật khẩu của bạn

### Bước 3: Đăng nhập

Nhấn nút **"Đăng nhập"** để vào hệ thống.

> 💡 **Lưu ý**: Hệ thống sử dụng JWT Token để bảo mật phiên làm việc của bạn trong 24 giờ.

---

## 🏠 Giao diện chính

Sau khi đăng nhập thành công, bạn sẽ thấy giao diện chính với 4 tab:

**[Chỗ dán ảnh: Giao diện chính với 4 tab]**

### Cấu trúc menu

1. 💬 **Hỗ trợ Trực tuyến** - Chat với trợ lý AI
2. 🗄️ **Kho tri thức** - Xem và tìm kiếm vector chunks
3. 📄 **Quản lý Tài liệu** - Xem danh sách tài liệu đã upload
4. ⬆️ **Tải lên Tài liệu** - Upload file mới vào hệ thống

### Header

- **Logo và tên hệ thống**: DVC.AI - Trợ lý dịch vụ công và cổng Kiến thức
- **Thông tin người dùng**: Hiển thị tên người dùng hiện tại
- **Menu người dùng**: 
  - Thông tin cá nhân
  - Cài đặt
  - Đăng xuất

---

## 💬 Hỗ trợ Trực tuyến

Tab **Hỗ trợ Trực tuyến** là nơi bạn có thể trò chuyện với trợ lý AI DVC.AI.

**[Chỗ dán ảnh: Giao diện chat với trợ lý AI]**

### 🌟 Tính năng

#### 1. Trò chuyện tự nhiên
- Gõ câu hỏi của bạn vào ô chat
- AI sẽ trả lời một cách thân thiện, dễ thương và đầy tình cảm
- Hỗ trợ tiếng Việt hoàn toàn tự nhiên

#### 2. Câu hỏi thường gặp
Hệ thống cung cấp 16 câu hỏi mẫu về các thủ tục phổ biến:

- ✅ Làm thế nào để cấp xác nhận số CMND 09 số?
- ✅ Quy trình trình báo mất hộ chiếu như thế nào?
- ✅ Thủ tục thông báo lưu trú cần làm gì?
- ✅ Cách khôi phục giá trị sử dụng hộ chiếu đã mất?
- ✅ Làm căn cước công dân cho người từ 14 tuổi cần gì?
- ✅ Cấp đổi thẻ căn cước có mất phí không?
- ✅ Cấp lại thẻ căn cước khi bị mất thì làm sao?
- ✅ Gia hạn tạm trú phải làm trước bao nhiêu ngày?
- ✅ Làm hộ chiếu phổ thông tốn bao nhiêu tiền?
- ✅ Có thể nộp hồ sơ trực tuyến không?
- ✅ Thu thập sinh trắc học khi làm căn cước là gì?
- ✅ Thời gian làm hộ chiếu bao lâu?
- ✅ Cấp thẻ căn cước tại cấp tỉnh hay trung ương?
- ✅ Thẻ căn cước hết hạn thì phải làm gì?
- ✅ Có thể làm hộ chiếu ở tỉnh khác không?
- ✅ Miễn phí thủ tục nào về căn cước?

**[Chỗ dán ảnh: Danh sách câu hỏi thường gặp]**

#### 3. Nguồn tham khảo
Mỗi câu trả lời của AI đều kèm theo:
- 📊 **Tag RAG/NORMAL**: Cho biết AI có sử dụng dữ liệu từ kho tri thức không
- 📚 **Nguồn tài liệu**: Số lượng nguồn tham khảo được sử dụng
- 🔍 **Xem chi tiết**: Click vào để xem nội dung chi tiết từ các nguồn

**[Chỗ dán ảnh: Tin nhắn với tag RAG và nguồn tài liệu]**

#### 4. Trạng thái kết nối
- 🟢 **Trực tuyến**: WebSocket đang hoạt động (real-time)
- 🟠 **Kết nối HTTP**: Sử dụng REST API (vẫn hoạt động tốt)

#### 5. Xóa lịch sử chat
- Nhấn nút 🔄 **Refresh** để bắt đầu cuộc trò chuyện mới
- Lịch sử cũ sẽ bị xóa và AI bắt đầu lại từ đầu

### 📝 Cách sử dụng

1. **Nhập câu hỏi**: Gõ câu hỏi vào ô nhập ở cuối màn hình
2. **Gửi tin nhắn**: Nhấn Enter hoặc nút gửi
3. **Đợi phản hồi**: AI sẽ xử lý và trả lời trong vài giây
4. **Xem nguồn**: Click vào số nguồn để xem tài liệu tham khảo
5. **Tiếp tục hỏi**: AI ghi nhớ ngữ cảnh cuộc trò chuyện

### 💡 Mẹo sử dụng

- ✨ Hỏi câu hỏi cụ thể: "Làm thẻ căn cước cần những giấy tờ gì?"
- 📋 Hỏi về quy trình: "Quy trình làm hộ chiếu có những bước nào?"
- 💰 Hỏi về phí: "Làm căn cước tốn bao nhiêu tiền?"
- ⏰ Hỏi về thời gian: "Làm hộ chiếu mất bao lâu?"
- 🏛️ Hỏi về địa điểm: "Làm thủ tục ở đâu?"

---

## 🗄️ Kho tri thức

Tab **Kho tri thức** hiển thị tất cả các đoạn văn bản (chunks) được lưu trong Vector Database để AI tìm kiếm và trả lời câu hỏi.

**[Chỗ dán ảnh: Giao diện Kho tri thức]**

### 🌟 Tính năng

#### 1. Thống kê tổng quan

Hiển thị ở đầu trang:
- 📊 **Tổng số chunks**: Tổng số đoạn văn bản trong hệ thống
- 📁 **Số file unique**: Số lượng file gốc
- 📈 **Trung bình chunks/file**: Mỗi file được chia thành bao nhiêu chunks

**[Chỗ dán ảnh: Thống kê tổng quan]**

#### 2. Tìm kiếm chunks

- **Tìm kiếm theo nội dung**: Nhập từ khóa hoặc câu hỏi
- **Lọc theo file**: Chọn file cụ thể để xem chunks của file đó
- **Số lượng kết quả**: Chọn hiển thị 10/20/50/100 kết quả

**[Chỗ dán ảnh: Thanh tìm kiếm và bộ lọc]**

#### 3. Bảng danh sách chunks

Hiển thị thông tin chi tiết:
- **File Name**: Tên file gốc
- **Chunk ID**: Số thứ tự của chunk
- **Section**: Phần/mục của chunk
- **Content Preview**: Xem trước nội dung (200 ký tự đầu)
- **Content Length**: Độ dài nội dung (ký tự)
- **Thao tác**: Nút "Xem chi tiết"

**[Chỗ dán ảnh: Bảng danh sách chunks]**

#### 4. Xem chi tiết chunk

Click vào **"Xem chi tiết"** để xem nội dung đầy đủ:
- Hiển thị trong popup
- Format đẹp với Markdown
- Có thể cuộn để đọc hết nội dung

**[Chỗ dán ảnh: Popup xem chi tiết chunk]**

#### 5. Phân trang

- Chọn số trang để xem các chunks khác
- Hiển thị tổng số chunks

### 📝 Cách sử dụng

1. **Xem tổng quan**: Kiểm tra số liệu thống kê ở đầu trang
2. **Tìm kiếm**: Nhập từ khóa vào ô tìm kiếm
3. **Lọc**: Chọn file cụ thể nếu cần
4. **Xem chi tiết**: Click "Xem chi tiết" để đọc nội dung đầy đủ
5. **Refresh**: Nhấn nút 🔄 để tải lại dữ liệu mới

---

## 📄 Quản lý Tài liệu

Tab **Quản lý Tài liệu** cho phép bạn xem và quản lý tất cả các tài liệu đã upload vào hệ thống.

**[Chỗ dán ảnh: Giao diện Quản lý Tài liệu]**

### 🌟 Tính năng

#### 1. Thống kê tổng quan

Hiển thị ở đầu trang với 3 chỉ số quan trọng:
- 📊 **Tổng tài liệu**: Tổng số file trong hệ thống
- ⬆️ **Hôm nay**: Số file được upload trong ngày
- 📈 **Tuần này**: Số file được upload trong tuần

**[Chỗ dán ảnh: Thống kê tổng quan tài liệu]**

#### 2. Bảng danh sách tài liệu

Hiển thị thông tin chi tiết về từng tài liệu:

| Cột | Mô tả |
|-----|-------|
| **STT** | Số thứ tự |
| **Tên file** | Tên file với icon tương ứng (PDF, Word, TXT, Image) |
| **Loại file** | Định dạng file (PDF, DOCX, DOC, TXT, MD, PNG, JPG) |
| **Kích thước** | Dung lượng file (KB/MB) |
| **Ngày upload** | Thời gian upload file |
| **Trạng thái** | Đang xử lý / Hoàn tất |
| **Thao tác** | Nút xóa file |

**[Chỗ dán ảnh: Bảng danh sách tài liệu]**

#### 3. Icon theo loại file

Hệ thống tự động hiển thị icon phù hợp:
- 📕 **PDF**: Icon màu đỏ
- 📘 **Word**: Icon màu xanh (DOCX, DOC)
- 📄 **Text**: Icon màu xám (TXT, MD)
- 🖼️ **Image**: Icon màu xanh lá (PNG, JPG, JPEG)

#### 4. Trạng thái xử lý

Mỗi file có trạng thái:
- ⚙️ **Đang xử lý**: File đang được xử lý bởi AI (hiển thị progress bar)
- ✅ **Hoàn tất**: File đã được xử lý và lưu vào database

**[Chỗ dán ảnh: File đang xử lý với progress bar]**

#### 5. Xóa tài liệu

- Nhấn nút **Xóa** ở cột thao tác
- Xác nhận trong popup
- Tài liệu sẽ bị xóa khỏi hệ thống và Vector Database

### 📝 Cách sử dụng

1. **Xem danh sách**: Tất cả tài liệu hiển thị trong bảng
2. **Kiểm tra trạng thái**: Xem file nào đang xử lý, file nào đã xong
3. **Xóa tài liệu**: Nhấn nút xóa và xác nhận
4. **Làm mới**: Nhấn nút 🔄 Làm mới để cập nhật danh sách

### ⚠️ Lưu ý quan trọng

- Việc xóa tài liệu **không thể hoàn tác**
- File đã xóa sẽ bị xóa khỏi cả Vector Database
- Hệ thống tự động cập nhật khi có file mới được upload

---

## ⬆️ Tải lên Tài liệu

Tab **Tải lên Tài liệu** cho phép bạn upload file vào hệ thống để AI xử lý và lưu vào kho tri thức.

**[Chỗ dán ảnh: Giao diện Upload tài liệu]**

### 🌟 Tính năng

#### 1. Upload file đơn lẻ

**Vùng kéo thả file (Drag & Drop):**
- Kéo file vào vùng upload
- Hoặc click để chọn file từ máy tính
- Hỗ trợ upload 1 file tại một thời điểm

**[Chỗ dán ảnh: Vùng drag & drop]**

#### 2. Upload nhiều file (Bulk Upload)

**Tải lên nhiều file cùng lúc:**
- Click nút **"Chọn nhiều file"**
- Chọn nhiều file cùng lúc (Ctrl + Click)
- Upload tất cả cùng một lần

**[Chỗ dán ảnh: Upload nhiều file]**

#### 3. Định dạng file được hỗ trợ

Hệ thống hỗ trợ đa dạng định dạng:

| Loại | Định dạng | Kích thước tối đa |
|------|-----------|-------------------|
| 📕 **Tài liệu PDF** | `.pdf` | 100 MB |
| 📘 **Microsoft Word** | `.docx`, `.doc` | 100 MB |
| 📄 **Văn bản** | `.txt`, `.md` | 100 MB |
| 🖼️ **Hình ảnh** | `.png`, `.jpg`, `.jpeg` | 100 MB |

> 💡 **Lưu ý**: Đối với file `.doc` cũ (Word 97-2003), hệ thống sẽ tự động xử lý nhưng khuyến nghị chuyển sang `.docx` để đạt chất lượng tốt nhất.

#### 4. Theo dõi tiến trình Upload

**Real-time Progress Tracking:**
- **WebSocket Real-time**: Theo dõi tiến trình ngay lập tức
- **Progress Bar**: Hiển thị phần trăm hoàn thành
- **Thông báo**: Thông báo khi upload thành công/thất bại

**Các giai đoạn xử lý:**

1. ⬆️ **Uploading** (0-30%): Đang tải file lên server
2. ☁️ **Saving to Cloud** (30-50%): Lưu file lên Google Cloud Storage
3. 🔄 **Processing** (50-80%): AI đang trích xuất nội dung
4. 🗄️ **Indexing** (80-100%): Lưu vào Vector Database
5. ✅ **Complete** (100%): Hoàn tất!

**[Chỗ dán ảnh: Progress bar chi tiết từng giai đoạn]**

#### 5. Kết quả Upload

Sau khi upload thành công, hệ thống hiển thị:
- ✅ Tên file đã upload
- 📊 Số lượng chunks được tạo
- 💾 Kích thước file
- 🎉 Thông báo thành công

**[Chỗ dán ảnh: Thông báo upload thành công]**

### 📝 Hướng dẫn Upload

#### Upload file đơn lẻ

1. **Chuẩn bị file**: Đảm bảo file đúng định dạng và dưới 100MB
2. **Kéo thả hoặc chọn**: 
   - Kéo file vào vùng "Click hoặc kéo file vào đây"
   - Hoặc click vào vùng đó để chọn file
3. **Đợi xử lý**: 
   - Xem progress bar để biết tiến trình
   - File sẽ được xử lý qua 4 giai đoạn
4. **Kiểm tra kết quả**: 
   - Thông báo thành công xuất hiện
   - File được thêm vào "Quản lý Tài liệu"
   - Nội dung được lưu vào "Kho tri thức"

#### Upload nhiều file (Bulk Upload)

1. **Click "Chọn nhiều file"**: Mở cửa sổ chọn file
2. **Chọn nhiều file**: Giữ Ctrl (Windows) hoặc Cmd (Mac) và click chọn nhiều file
3. **Xác nhận**: Nhấn Open
4. **Theo dõi tiến trình**: 
   - Hiển thị số file đã xử lý / tổng số file
   - Progress bar tổng thể
   - Danh sách chi tiết từng file
5. **Hoàn tất**: Tất cả file được xử lý và thêm vào hệ thống

**[Chỗ dán ảnh: Bulk upload với nhiều file]**

### 🔍 AI Document Processing

Khi bạn upload file, AI sẽ tự động:

#### 📄 Xử lý Text Documents (PDF, DOCX, DOC, TXT, MD)
1. Trích xuất toàn bộ văn bản
2. Phát hiện và bảo toàn cấu trúc (tiêu đề, đoạn văn)
3. Trích xuất nội dung từ bảng biểu
4. Chia nhỏ thành chunks (đoạn 3000 ký tự)
5. Tạo embeddings cho mỗi chunk
6. Lưu vào Vector Database

#### 🖼️ Xử lý Image Documents (PNG, JPG, JPEG)
1. **OCR (Tesseract)**: Nhận dạng chữ trong ảnh
2. **AI Vision (GPT-4o)**: Phân tích hình ảnh, bảng biểu, sơ đồ
3. Kết hợp kết quả OCR + AI Vision
4. Chia nhỏ và tạo embeddings
5. Lưu vào Vector Database

**[Chỗ dán ảnh: Quy trình xử lý file với AI]**

### ⚠️ Lưu ý quan trọng

- ⚡ **Thời gian xử lý**: Tùy thuộc vào kích thước file (2-30 giây)
- 📊 **File lớn**: File càng lớn, thời gian xử lý càng lâu
- 🖼️ **Image**: File ảnh mất nhiều thời gian hơn vì cần OCR + AI Vision
- 🔄 **WebSocket**: Đảm bảo kết nối Internet ổn định để nhận cập nhật real-time
- 💾 **Lưu trữ**: File được lưu cả trên Cloud Storage và Vector Database

### ❌ Xử lý lỗi

Nếu upload thất bại:
- ❌ Kiểm tra định dạng file có hỗ trợ không
- ❌ Kiểm tra kích thước file < 100MB
- ❌ Kiểm tra kết nối Internet
- ❌ Thử upload lại

---

## 🔍 Cách thức hoạt động của AI

### 🧠 Công nghệ RAG (Retrieval-Augmented Generation)

DVC.AI sử dụng công nghệ RAG tiên tiến để trả lời câu hỏi:

#### Quy trình xử lý câu hỏi:

1. **📝 Nhận câu hỏi**: Bạn gửi câu hỏi cho AI
2. **🔍 Tìm kiếm ngữ nghĩa**: AI tìm kiếm các chunks liên quan trong Vector Database
3. **📊 Đánh giá độ liên quan**: Tính toán độ tương đồng (similarity score)
4. **🎯 Chọn nguồn tốt nhất**: Lấy top 5-10 chunks liên quan nhất
5. **🤖 Sinh câu trả lời**: GPT-4o đọc các nguồn và tạo câu trả lời
6. **💬 Trả lời**: Gửi câu trả lời kèm nguồn tham khảo cho bạn

**[Chỗ dán ảnh: Sơ đồ quy trình RAG]**

### 🎯 Ưu điểm của RAG

- ✅ **Chính xác**: Dựa trên dữ liệu thực tế, không bịa đặt
- ✅ **Có nguồn**: Mỗi câu trả lời đều có tài liệu tham khảo
- ✅ **Cập nhật**: Thêm file mới → AI biết ngay lập tức
- ✅ **Linh hoạt**: Trả lời theo ngữ cảnh và lịch sử hội thoại

### 💾 Vector Database (Milvus)

**Vector Database** là công nghệ lưu trữ đặc biệt:
- Chuyển văn bản thành vector (dãy số)
- Tính toán độ tương đồng giữa các vector
- Tìm kiếm theo ngữ nghĩa, không chỉ từ khóa

**Ví dụ:**
- Câu hỏi: "Làm hộ chiếu tốn bao nhiêu?"
- Tìm được: "Lệ phí hộ chiếu 160.000 - 200.000 đồng"
- Mặc dù không có từ "tốn" trong văn bản gốc!

---

## 🎓 Câu hỏi thường gặp

### ❓ Hệ thống

**Q: Tôi có thể sử dụng hệ thống trên điện thoại không?**
A: Có! Giao diện DVC.AI responsive, hoạt động tốt trên mọi thiết bị.

**Q: Làm sao để đăng xuất?**
A: Click vào avatar ở góc phải trên → Chọn "Đăng xuất".

**Q: Thông tin của tôi có bảo mật không?**
A: Có! Hệ thống sử dụng JWT Token và mã hóa kết nối.

### ❓ Chat với AI

**Q: AI trả lời có chính xác không?**
A: Có! AI chỉ trả lời dựa trên tài liệu có trong hệ thống, kèm theo nguồn tham khảo.

**Q: AI có nhớ cuộc trò chuyện trước không?**
A: Có! AI ghi nhớ 8-10 tin nhắn gần nhất để hiểu ngữ cảnh.

**Q: Làm sao để bắt đầu cuộc trò chuyện mới?**
A: Nhấn nút 🔄 Refresh ở góc trên phải của chat.

**Q: Tại sao có tag "RAG" và "NORMAL"?**
- **RAG**: AI đã tìm kiếm và sử dụng thông tin từ kho tri thức
- **NORMAL**: AI trả lời trực tiếp, không cần tìm kiếm

**Q: Làm sao xem nguồn tài liệu AI đã tham khảo?**
A: Click vào số nguồn (ví dụ: "3 nguồn") bên dưới tin nhắn.

### ❓ Upload và xử lý file

**Q: File nào có thể upload?**
A: PDF, DOCX, DOC, TXT, MD (Markdown), PNG, JPG, JPEG - tối đa 100MB.

**Q: Tại sao file .doc của tôi không xử lý được?**
A: File `.doc` cũ (Word 97-2003) có thể gặp vấn đề. Khuyến nghị chuyển sang `.docx`.

**Q: Upload file mất bao lâu?**
A: 
- File text nhỏ: 2-5 giây
- File PDF trung bình: 5-15 giây
- File ảnh: 10-30 giây (cần OCR + AI Vision)

**Q: Tại sao upload chậm?**
A: 
- AI đang trích xuất nội dung (OCR cho ảnh)
- Đang tạo embeddings cho từng chunk
- Đang lưu vào Vector Database
- File lớn hoặc nhiều trang sẽ mất nhiều thời gian hơn

**Q: Có thể upload nhiều file cùng lúc không?**
A: Có! Sử dụng chức năng Bulk Upload (chọn nhiều file).

**Q: File đã upload có thể tải xuống không?**
A: Hiện tại chưa hỗ trợ download, chỉ hỗ trợ xem và xóa.

### ❓ Kho tri thức

**Q: "Chunk" là gì?**
A: Chunk là đoạn văn bản nhỏ (khoảng 3000 ký tự) được chia từ tài liệu gốc để AI dễ tìm kiếm và xử lý.

**Q: Tại sao 1 file lại có nhiều chunks?**
A: File lớn được chia nhỏ để:
- AI tìm kiếm chính xác hơn
- Phù hợp với giới hạn của OpenAI (8192 tokens)
- Tăng tốc độ xử lý

**Q: Làm sao tìm kiếm trong Kho tri thức?**
A: Nhập từ khóa hoặc câu hỏi vào ô tìm kiếm, hệ thống sẽ tìm các chunks liên quan.

**Q: Có thể xem nội dung đầy đủ của chunk không?**
A: Có! Click nút "Xem chi tiết" để xem toàn bộ nội dung.

### ❓ Xử lý sự cố

**Q: Màn hình bị trống/không load được?**
A: 
- Kiểm tra kết nối Internet
- Thử reload (F5) trang
- Xóa cache trình duyệt (Ctrl + Shift + Delete)
- Đăng xuất và đăng nhập lại

**Q: Upload file bị lỗi?**
A:
- Kiểm tra định dạng file
- Kiểm tra kích thước < 100MB
- Thử upload lại
- Liên hệ quản trị viên nếu vẫn lỗi

**Q: AI không trả lời?**
A:
- Kiểm tra kết nối mạng
- Xem trạng thái kết nối (Trực tuyến/HTTP)
- Thử hỏi câu khác
- Reload (F5) trang

**Q: Không thấy file vừa upload?**
A:
- Đợi 5-10 giây để hệ thống xử lý xong
- Nhấn nút 🔄 Làm mới
- Chuyển sang tab "Quản lý Tài liệu" để kiểm tra

---

## 💡 Tips & Tricks

### 🎯 Hỏi AI hiệu quả

**✅ Câu hỏi tốt:**
- "Thủ tục làm hộ chiếu phổ thông cần những giấy tờ gì?"
- "Thời gian xử lý hồ sơ căn cước là bao lâu?"
- "Lệ phí làm thẻ căn cước bao nhiêu tiền?"

**❌ Câu hỏi chưa tốt:**
- "Hộ chiếu" (quá ngắn, không rõ ý)
- "Giấy tờ" (quá chung chung)

### 📁 Upload tài liệu hiệu quả

- ✅ Upload từng file để theo dõi tiến trình dễ dàng
- ✅ Đặt tên file có ý nghĩa: "Thu_tuc_ho_chieu.pdf"
- ✅ Chuyển file .doc → .docx trước khi upload
- ✅ Nén ảnh lớn trước khi upload
- ✅ Sử dụng Bulk Upload cho nhiều file nhỏ

### 🔍 Tìm kiếm trong Kho tri thức

- ✅ Dùng từ khóa cụ thể: "hộ chiếu", "căn cước", "lưu trú"
- ✅ Lọc theo file để tìm nhanh hơn
- ✅ Xem chi tiết chunk để đọc ngữ cảnh đầy đủ

---

## 📞 Hỗ trợ kỹ thuật

### 🆘 Khi cần trợ giúp

Nếu bạn gặp vấn đề khi sử dụng hệ thống:

1. **Thử các bước cơ bản**:
   - Reload (F5) trang
   - Đăng xuất và đăng nhập lại
   - Xóa cache trình duyệt
   - Thử trình duyệt khác

2. **Kiểm tra kết nối**:
   - Đảm bảo Internet ổn định
   - Kiểm tra tường lửa/firewall
   - Thử tắt VPN nếu có

3. **Liên hệ quản trị viên**:
   - Cung cấp thông tin: Tên đăng nhập, thời gian lỗi, mô tả chi tiết
   - Kèm screenshot nếu có thể

### 📚 Tài liệu bổ sung

Xem thêm tài liệu kỹ thuật chi tiết tại:
- Kiến trúc hệ thống: `docs/ARCHITECTURE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- Quick Start: `docs/QUICK_START.md`

---

## 🎉 Bắt đầu sử dụng!

DVC.AI sẵn sàng hỗ trợ bạn 24/7 với công nghệ AI tiên tiến!

### 🚀 Các bước đầu tiên:

1. ✅ **Đăng nhập** vào hệ thống
2. 💬 **Trò chuyện** với AI để làm quen
3. ⬆️ **Upload** một vài tài liệu thử
4. 🔍 **Khám phá** Kho tri thức
5. 🎯 **Hỏi** những câu hỏi thực tế

> 💙 **DVC.AI luôn sẵn sàng hỗ trợ bạn! Hãy thử ngay hôm nay!** 😊

---

## 📝 Thông tin phiên bản

- **Version**: 3.1.0
- **Cập nhật**: 2025
- **Công nghệ**: React.js, FastAPI, OpenAI GPT-4o, Milvus Vector DB
- **Tính năng mới**:
  - ✨ Chatbot có tình cảm và dễ thương hơn
  - 🗄️ Đổi tên "Vector Chunks" thành "Kho tri thức"
  - 🎯 16 câu hỏi thường gặp dựa trên dữ liệu thực tế
  - 🔄 Sắp xếp lại menu: Hỗ trợ trực tuyến lên đầu
  - 📄 Hỗ trợ file .doc cũ (Word 97-2003)
  - 🔧 Cải thiện chunking cho file lớn

---

**© 2025 DVC.AI - Virtual Assistant Platform**

*Hướng dẫn này được tạo tự động từ source code hệ thống.*

