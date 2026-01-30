![alt text](/desktop/assets/icons/logo.ico)

**Project Overview**
- **Mô tả:** Ứng dụng desktop giúp đo các hình dạng trong ảnh bằng sức mạnh AI. Hỗ trợ nhập ảnh, vẽ vùng đo, và xuất kết quả đo.
- **Mục đích**: Hỗ trợ các ngành cần tính diện tích các hình phức tạp, không có hình dạng rõ ràng, các mảnh đất, các vật thể 2D, ...
- **Công thức tính toán**: Dự án sử dụng cách tính diện tích bằng cách quy đổi giữa điểm ảnh (pixel)/số liệu thật, bằng cách này chúng ta có thể tính diện tích của vật thể rất đơn giản

**Features**
- **Đo tự động:** Phát hiện và đo kích thước của các hình dạng cơ bản và phức tạp.
- **Chế độ thủ công:** Cho phép người dùng chỉnh sửa vùng đo bằng công cụ vẽ.
- **Xuất kết quả:** Lưu ảnh kết quả và/hoặc xuất số liệu đo.
- **Mô hình nội bộ:** Sử dụng mô hình có sẵn trong `desktop/assets/models` để xử lý.

**Yêu cầu**
- Python 3.10+ (khuyến nghị).
- Conda cài môi trường.
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
1. Giao diện chính
![alt text](/desktop/results/1.png)
2. Phân đoạn hình muốn đo diện tích
![alt text](/desktop/results/2.png)
3. Sau đó ta sẽ áp dụng thước đo, để quy đổi thành kích thước thất
![alt text](/desktop/results/3.png)
4. Cuối màn hình ta sẽ thấy tỉ lệ pixel/cm và kết quả diện tích
![alt text](/desktop/results/4.png)
5. Mode vẽ hình, ở đây ta có thể vẽ bất kì hình dạng nào ta muốn
![alt text](/desktop/results/5.png)
6. Sau khi vẽ hình xong, sẽ tự động xuất output ra phía bên phải
![alt text](/desktop/results/6.png)
7. Và setup thước đo, tính toán như bình thường
![alt text](/desktop/results/7.png)
8. Ở đây ta có thể cấu hình để vẽ các hình thẳng hơn, dễ dàng hơn cho người dùng
![alt text](/desktop/results/8.png)
9. Đây là các chế độ trong mode vẽ hình này gồm có Hiện Grid, Bắt Điểm, phóng to thu nhỏ ô lưới và cọ vẽ
![alt text](/desktop/results/10.png)
---
Phiên bản README: cập nhật bởi nhóm phát triển.