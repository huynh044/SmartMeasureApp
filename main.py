import sys
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

# 1. Thêm đường dẫn gốc vào hệ thống để Python tìm được thư mục 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
# Import giao diện chính từ thư mục src/gui/windows
from src.gui.windows.main_window import MainWindow 

if __name__ == "__main__":
    # Khởi tạo ứng dụng
    app = QApplication(sys.argv)
    
    # Thiết lập Font chữ Inter cho toàn bộ ứng dụng
    app.setFont(QFont("Inter", 10))
    
    # Thiết lập Icon cho thanh Taskbar
    icon_path = os.path.join(current_dir, "assets", "icons", "logo.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Hiển thị cửa sổ chính
    window = MainWindow()
    window.show()
    
    # Chạy vòng lặp sự kiện
    sys.exit(app.exec())