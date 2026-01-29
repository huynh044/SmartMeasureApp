import sys
import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QWidget, QFileDialog, 
                             QMessageBox, QLabel, QInputDialog, QComboBox, 
                             QSplitter, QSlider, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt
from src.gui.widgets.canvas import SmartCanvas
from src.engine.ai_processor import AIProcessor
from src.engine.geometry import GeometryUtils

DARK_THEME = """
QMainWindow { background-color: #2b2b2b; }
QWidget { color: #ffffff; font-family: 'Inter'; font-size: 14px; }
QPushButton {
    background-color: #404040; border: 1px solid #555;
    border-radius: 5px; padding: 8px; color: white;
}
QPushButton:hover { background-color: #505050; border: 1px solid #777; }
QPushButton:checked { background-color: #0078d4; border: 1px solid #005a9e; }
QLabel { color: #e0e0e0; font-weight: bold;}
QComboBox { background-color: #404040; color: white; padding: 5px; }
QSlider::groove:horizontal { height: 8px; background: #404040; border-radius: 4px; }
QSlider::handle:horizontal { background: #0078d4; width: 16px; margin: -4px 0; border-radius: 8px; }
QGroupBox { border: 1px solid #555; border-radius: 5px; margin-top: 10px; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Measure Pro - Dark Edition")
        self.setGeometry(50, 50, 1500, 900)
        self.setStyleSheet(DARK_THEME)

        try:
            self.ai_processor = AIProcessor()
            self.ai_ready = True
        except Exception as e:
            self.ai_ready = False
            QMessageBox.critical(self, "Lỗi AI", str(e))

        self.original_image = None
        self.current_mask = None
        self.scale_factor = None 
        self.current_unit = "cm"

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # --- 1. TOOLBAR ---
        toolbar = QHBoxLayout()
        
        # Nhóm File
        self.btn_open = QPushButton("📂 Mở Ảnh")
        self.btn_open.clicked.connect(self.open_image)
        
        self.btn_blank = QPushButton("🎨 Bảng Vẽ")
        self.btn_blank.clicked.connect(self.create_blank_mode)

        # Nhóm Đơn vị
        self.combo_unit = QComboBox()
        self.combo_unit.addItems(["cm", "mm", "m", "inch"])
        self.combo_unit.currentTextChanged.connect(self.change_unit)

        # Nhóm AI Tools
        self.btn_box = QPushButton("🔲 AI Box")
        self.btn_box.setCheckable(True)
        self.btn_box.clicked.connect(lambda: self.set_input_mode("BOX"))

        self.btn_point = QPushButton("📍 AI Click")
        self.btn_point.setCheckable(True)
        self.btn_point.clicked.connect(lambda: self.set_input_mode("POINT"))

        # Nhóm Vẽ Tay (Mới)
        self.btn_paint = QPushButton("✏️ Vẽ Tay")
        self.btn_paint.setCheckable(True)
        self.btn_paint.clicked.connect(lambda: self.set_input_mode("PAINT"))

        # Nút Chuyển Vẽ -> Đo
        self.btn_finish_draw = QPushButton("✅ Đo hình này")
        self.btn_finish_draw.setStyleSheet("background-color: #28a745; color: white;")
        self.btn_finish_draw.clicked.connect(self.process_drawn_image)
        self.btn_finish_draw.hide() # Chỉ hiện khi ở chế độ vẽ

        # Nhóm Output
        self.btn_ruler = QPushButton("📏 Đo Đạc")
        self.btn_ruler.setCheckable(True)
        self.btn_ruler.clicked.connect(self.enable_ruler_mode)
        
        self.btn_clear = QPushButton("🔄 Reset")
        self.btn_clear.clicked.connect(self.clear_measurements)

        # Thêm nút vào Toolbar
        widgets = [self.btn_open, self.btn_blank, QLabel("|"), 
                   QLabel("Đơn vị:"), self.combo_unit, QLabel("|"),
                   self.btn_box, self.btn_point, self.btn_paint, self.btn_finish_draw, QLabel("|"),
                   self.btn_ruler, self.btn_clear]
        for w in widgets:
            toolbar.addWidget(w)
        toolbar.addStretch()

        # --- 2. SETTINGS PANEL (Cho chế độ vẽ) ---
        self.panel_settings = QWidget()
        layout_sets = QHBoxLayout(self.panel_settings)
        layout_sets.setContentsMargins(0,0,0,0)
        
        # Setting Lưới
        self.chk_grid = QCheckBox("Hiện Lưới")
        self.chk_grid.toggled.connect(self.toggle_grid_display)
        
        self.chk_snap = QCheckBox("Bắt điểm (Snap)")
        self.chk_snap.toggled.connect(self.toggle_snap)
        
        lbl_grid_size = QLabel("Cỡ Lưới:")
        self.slider_grid = QSlider(Qt.Orientation.Horizontal)
        self.slider_grid.setRange(10, 200) # 10px đến 200px
        self.slider_grid.setValue(50)
        self.slider_grid.valueChanged.connect(self.update_grid_size)

        # Setting Nét Vẽ
        lbl_brush = QLabel("Nét Vẽ:")
        self.slider_brush = QSlider(Qt.Orientation.Horizontal)
        self.slider_brush.setRange(1, 50)
        self.slider_brush.setValue(5)
        self.slider_brush.valueChanged.connect(self.update_brush_size)

        for w in [self.chk_grid, self.chk_snap, lbl_grid_size, self.slider_grid, QLabel("|"), lbl_brush, self.slider_brush]:
            layout_sets.addWidget(w)
        layout_sets.addStretch()
        self.panel_settings.hide() # Ẩn mặc định

        # --- 3. CANVAS ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.canvas_input = SmartCanvas(is_input=True)
        self.canvas_input.request_mask_point.connect(self.run_ai_point)
        self.canvas_input.request_mask_box.connect(self.run_ai_box)
        
        self.canvas_output = SmartCanvas(is_input=False)
        self.canvas_output.ruler_updated.connect(self.handle_measurement)

        splitter.addWidget(self.canvas_input)
        splitter.addWidget(self.canvas_output)
        splitter.setSizes([700, 700])

        # --- 4. BOTTOM ---
        bottom_layout = QHBoxLayout()
        self.lbl_status = QLabel("Sẵn sàng.")
        self.lbl_area_result = QLabel("")
        self.lbl_area_result.setStyleSheet("color: #00ff00; font-size: 16px; font-weight: bold;")
        bottom_layout.addWidget(self.lbl_status)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.lbl_area_result)

        # Main Layout Assembly
        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.panel_settings)
        main_layout.addWidget(splitter, 1)
        main_layout.addLayout(bottom_layout)

        self.toggle_buttons(False)

    def toggle_buttons(self, state):
        self.btn_point.setEnabled(state)
        self.btn_box.setEnabled(state)
        self.btn_paint.setEnabled(state)
        self.btn_ruler.setEnabled(state)
        self.btn_clear.setEnabled(state)

    def change_unit(self, unit):
        self.current_unit = unit
        self.scale_factor = None
        self.lbl_status.setText(f"Đơn vị: {unit}. Vui lòng đo lại.")

    # --- INPUT MODES ---
    def set_input_mode(self, mode):
        self.canvas_input.mode = mode
        self.canvas_output.mode = "VIEW"
        
        # UI Toggles
        self.btn_point.setChecked(mode == "POINT")
        self.btn_box.setChecked(mode == "BOX")
        self.btn_paint.setChecked(mode == "PAINT")
        self.btn_ruler.setChecked(False)

        # Logic hiển thị Panel và Nút
        if mode == "PAINT":
            self.panel_settings.show()
            self.btn_finish_draw.show()
            self.lbl_status.setText("Chế độ Vẽ: Giữ chuột trái để vẽ. Dùng thanh trượt để chỉnh lưới.")
        else:
            self.panel_settings.hide()
            self.btn_finish_draw.hide()
            self.lbl_status.setText(f"Chế độ AI: {mode}")

    def create_blank_mode(self):
        """Chế độ Bảng Vẽ (Không cần ảnh)"""
        # Tạo canvas đen 1920x1080 (hoặc full HD)
        self.canvas_input.create_blank_canvas(1920, 1080)
        self.canvas_output.set_image(np.zeros((1080, 1920, 3), dtype=np.uint8))
        self.original_image = self.canvas_input.image # Ảnh gốc là cái bảng đen
        
        self.toggle_buttons(True)
        # Tự động bật chế độ vẽ
        self.chk_grid.setChecked(True) # Tự bật lưới cho dễ nhìn
        self.set_input_mode("PAINT")

    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Mở Ảnh", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            img = cv2.imread(path)
            if img is None: return
            self.original_image = img
            self.canvas_input.set_image(img)
            self.canvas_output.set_image(np.zeros_like(img))
            if self.ai_ready:
                self.ai_processor.set_image(img)
            
            self.toggle_buttons(True)
            self.set_input_mode("BOX")

    # --- GRID & PAINT SETTINGS ---
    def toggle_grid_display(self, checked):
        self.canvas_input.show_grid = checked
        self.canvas_input.update()

    def toggle_snap(self, checked):
        self.canvas_input.snap_to_grid = checked

    def update_grid_size(self, val):
        self.canvas_input.grid_size = val
        self.canvas_input.update()

    def update_brush_size(self, val):
        self.canvas_input.brush_size = val

    # --- PROCESSING ---
    def process_drawn_image(self):
        """Chuyển hình vẽ tay sang màn hình đo đạc (CÓ TỰ ĐỘNG TÔ ĐẦY)"""
        # 1. Lấy hình vẽ nét trắng nền đen
        drawn_img = self.canvas_input.image
        gray = cv2.cvtColor(drawn_img, cv2.COLOR_BGR2GRAY)
        
        # 2. Tạo mask nhị phân (chỉ còn 0 và 255)
        _, binary = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

        # 3. TỰ ĐỘNG TÔ ĐẦY (Flood Fill)
        # Nguyên lý: Tìm các đường viền khép kín và tô màu trắng vào trong
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Tạo một mask mới sạch sẽ để đổ màu
        filled_mask = np.zeros_like(binary)
        
        # Vẽ lại các đường viền đó nhưng chọn thickness = -1 (Tức là tô đặc ruột)
        cv2.drawContours(filled_mask, contours, -1, (255), thickness=cv2.FILLED)
        
        # 4. Gửi cái hình ĐẶC RUỘT đó sang bên phải
        self.process_ai_result(filled_mask)

    def run_ai_point(self, x, y):
        if not self.ai_ready: return
        mask = self.ai_processor.predict_click(x, y)
        self.process_ai_result(mask)

    def run_ai_box(self, x1, y1, x2, y2):
        if not self.ai_ready: return
        mask = self.ai_processor.predict_box(x1, y1, x2, y2)
        self.process_ai_result(mask)

    def process_ai_result(self, mask):
        if mask is None: return
        self.current_mask = mask
        self.canvas_output.set_white_object_result(mask)
        self.enable_ruler_mode()
        self.lbl_status.setText("Đã nhận diện hình. Hãy đo kích thước!")
        if self.scale_factor: self.calculate_total_area()

    # --- OUTPUT MODES ---
    def enable_ruler_mode(self):
        self.canvas_input.mode = "VIEW"
        self.canvas_output.mode = "RULER"
        self.btn_point.setChecked(False)
        self.btn_box.setChecked(False)
        self.btn_paint.setChecked(False)
        self.btn_ruler.setChecked(True)
        self.panel_settings.hide()
        self.lbl_status.setText("Chế độ Output: Vẽ thước đo")

    def handle_measurement(self, pixel_dist):
        if self.scale_factor is None:
            val, ok = QInputDialog.getDouble(self, "Định chuẩn", 
                f"Độ dài đoạn này là bao nhiêu {self.current_unit}?", 
                10.0, 0.01, 10000, 2)
            if ok:
                self.scale_factor = val / pixel_dist
                self.lbl_status.setText(f"Đã lưu tỉ lệ. 1 px = {self.scale_factor:.4f} {self.current_unit}")
                self.calculate_total_area()
        else:
            real_dist = pixel_dist * self.scale_factor
            self.lbl_status.setText(f"📏 Đo được: {real_dist:.2f} {self.current_unit}")

    def calculate_total_area(self):
        if self.current_mask is None or self.scale_factor is None: return
        white_pixels = np.count_nonzero(self.current_mask)
        real_area = white_pixels * (self.scale_factor ** 2)
        self.lbl_area_result.setText(f"📐 DIỆN TÍCH: {real_area:.2f} {self.current_unit}²")

    def clear_measurements(self):
        self.canvas_output.measurements = []
        self.canvas_output.update()
        # Reset luôn cả canvas vẽ tay nếu đang ở mode vẽ
        if self.canvas_input.mode == "PAINT":
             self.canvas_input.create_blank_canvas(1920, 1080)
             
        reply = QMessageBox.question(self, "Reset", "Xóa cả tỉ lệ chuẩn luôn nhé?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.scale_factor = None
            self.lbl_area_result.setText("")