![alt text](/desktop/assets/icons/logo.ico)

**Project Overview**
- **Mô tả:** Ứng dụng desktop giúp đo các hình dạng trong ảnh bằng sức mạnh AI. Hỗ trợ nhập ảnh, vẽ vùng đo, và xuất kết quả đo.

**Features**
- **Đo tự động:** Phát hiện và đo kích thước của các hình dạng cơ bản và phức tạp.
- **Chế độ thủ công:** Cho phép người dùng chỉnh sửa vùng đo bằng công cụ vẽ.
- **Xuất kết quả:** Lưu ảnh kết quả và/hoặc xuất số liệu đo.
- **Mô hình nội bộ:** Sử dụng mô hình có sẵn trong `desktop/assets/models` để xử lý.

**Yêu cầu**
- Python 3.10+ (khuyến nghị).
- Conda (tùy chọn) hoặc pip để cài môi trường.
- Tài nguyên mô hình: [desktop/assets/models/mobile_sam.pt](desktop/assets/models/mobile_sam.pt).

**Cài đặt**
Tạo môi trường (sử dụng `env.yml` có sẵn):

```powershell
conda env create -f desktop/env.yml
conda activate measureapp
```

**Chạy ứng dụng (Desktop)**
- Từ thư mục gốc của repository, chạy:

```powershell
python desktop/main.py
```

**Cấu trúc chính**
- **desktop/**: Ứng dụng desktop chính (giao diện, engine, assets).
- **desktop/src/**: Mã nguồn Python cho GUI và logic (ví dụ: `desktop/src/gui`, `desktop/src/engine`).
- **desktop/assets/**: Fonts, icons, models (ví dụ: [desktop/assets/models](desktop/assets/models)).
- **website/**: Phiên bản web của ứng dụng (backend + frontend).

**Ghi chú về mô hình**
- Mô hình chính: [desktop/assets/models/mobile_sam.pt](desktop/assets/models/mobile_sam.pt). Đặt mô hình này vào đúng thư mục nếu cần cập nhật.

**Giao diện ứng dụng**
![alt text](/desktop/results/1.png)
![alt text](/desktop/results/2.png)
![alt text](/desktop/results/3.png)
![alt text](/desktop/results/4.png)
![alt text](/desktop/results/5.png)
![alt text](/desktop/results/6.png)
![alt text](/desktop/results/7.png)
![alt text](/desktop/results/8.png)
![alt text](/desktop/results/9.png)
![alt text](/desktop/results/10.png)
---
Phiên bản README: cập nhật bởi nhóm phát triển.