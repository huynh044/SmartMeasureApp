from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
import cv2
import numpy as np
from src.engine.geometry import GeometryUtils

class SmartCanvas(QWidget):
    request_mask_point = pyqtSignal(int, int)
    request_mask_box = pyqtSignal(int, int, int, int)
    ruler_updated = pyqtSignal(float)
    drawing_finished = pyqtSignal() # Báo hiệu vẽ xong để chuyển sang đo

    def __init__(self, parent=None, is_input=True):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.is_input = is_input 

        self.image = None
        self.display_image = None
        self.scale_ratio = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Modes: VIEW, POINT, BOX, PAINT (New), RULER
        self.mode = "VIEW" 
        
        # Data cho AI / Ruler
        self.box_start = None
        self.box_current = None
        self.measurements = []
        self.current_ruler_start = None
        self.snapped_point = None
        self.contour = None

        # --- TÍNH NĂNG VẼ (PAINT) ---
        self.last_draw_pos = None
        self.brush_size = 5
        self.grid_size = 50       # Kích thước ô lưới (pixel)
        self.show_grid = False    # Bật/Tắt lưới
        self.snap_to_grid = False # Bật/Tắt chế độ bắt điểm lưới

    def create_blank_canvas(self, width=1920, height=1080):
        """Tạo một bảng đen để vẽ"""
        # Tạo ảnh đen (1 kênh màu cho nhẹ, hoặc 3 kênh RGB)
        blank = np.zeros((height, width, 3), dtype=np.uint8)
        self.set_image(blank)
        self.measurements = []
        self.contour = None

    def set_image(self, image_cv2):
        self.image = image_cv2
        if len(image_cv2.shape) == 3:
            self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        else:
            self.display_image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2RGB)
        self.update()

    def set_white_object_result(self, mask):
        self.set_image(mask)
        self.contour = GeometryUtils.get_contour(mask)

    def transform_pos(self, widget_pos):
        if self.image is None: return None
        img_x = int((widget_pos.x() - self.offset_x) / self.scale_ratio)
        img_y = int((widget_pos.y() - self.offset_y) / self.scale_ratio)
        h, w = self.image.shape[:2]
        img_x = max(0, min(img_x, w - 1))
        img_y = max(0, min(img_y, h - 1))
        return (img_x, img_y)

    def to_screen(self, pt):
        if pt is None: return None
        sx = int(pt[0] * self.scale_ratio) + self.offset_x
        sy = int(pt[1] * self.scale_ratio) + self.offset_y
        return QPoint(sx, sy)

    def apply_snap(self, x, y):
        """Hàm làm tròn tọa độ theo lưới (Snap)"""
        if not self.snap_to_grid or self.grid_size <= 0:
            return x, y
        
        # Làm tròn đến bội số gần nhất của grid_size
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        return snapped_x, snapped_y

    def paint_on_canvas(self, start_pos, end_pos):
        """Vẽ trực tiếp lên dữ liệu ảnh self.image"""
        if self.image is None: return
        
        # Vẽ đường màu TRẮNG (255, 255, 255) lên ảnh gốc
        # Lưu ý: OpenCV vẽ lên numpy array gốc
        cv2.line(self.image, start_pos, end_pos, (255, 255, 255), self.brush_size)
        
        # Cập nhật lại display_image để hiển thị
        self.display_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        if self.image is None:
            painter.setPen(QColor("#888888"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, 
                             "Trống" if self.is_input else "Kết quả")
            return

        w_widget, h_widget = self.width(), self.height()
        h_img, w_img = self.image.shape[:2]
        self.scale_ratio = min(w_widget / w_img, h_widget / h_img)
        display_w, display_h = int(w_img * self.scale_ratio), int(h_img * self.scale_ratio)
        self.offset_x, self.offset_y = (w_widget - display_w) // 2, (h_widget - display_h) // 2

        # 1. Vẽ Ảnh
        q_img = QImage(self.display_image.data, w_img, h_img, 3 * w_img, QImage.Format.Format_RGB888)
        target_rect = QRect(self.offset_x, self.offset_y, display_w, display_h)
        painter.drawImage(target_rect, q_img)

        # 2. VẼ LƯỚI (GRID) - Chỉ hiện khi bật
        if self.show_grid and self.is_input:
            painter.setPen(QPen(QColor(0, 255, 255, 50), 1, Qt.PenStyle.DotLine)) # Màu cyan mờ
            
            # Vẽ dọc
            for x in range(0, w_img, self.grid_size):
                p1 = self.to_screen((x, 0))
                p2 = self.to_screen((x, h_img))
                if p1 and p2: painter.drawLine(p1, p2)
            
            # Vẽ ngang
            for y in range(0, h_img, self.grid_size):
                p1 = self.to_screen((0, y))
                p2 = self.to_screen((w_img, y))
                if p1 and p2: painter.drawLine(p1, p2)

        # 3. Vẽ Box (Input)
        if self.is_input and self.mode == "BOX" and self.box_start and self.box_current:
            start_scr = self.to_screen(self.box_start)
            curr_scr = self.to_screen(self.box_current)
            painter.setPen(QPen(QColor("cyan"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(QColor(0, 255, 255, 50))
            painter.drawRect(QRect(start_scr, curr_scr))

        # 4. Vẽ Thước (Output)
        if not self.is_input:
            pen_ruler = QPen(QColor(180, 0, 0), 3)
            painter.setPen(pen_ruler)
            for p1, p2 in self.measurements:
                painter.drawLine(self.to_screen(p1), self.to_screen(p2))
                painter.setBrush(QColor(180, 0, 0))
                painter.drawEllipse(self.to_screen(p1), 4, 4)
                painter.drawEllipse(self.to_screen(p2), 4, 4)

            if self.mode == "RULER" and self.current_ruler_start and self.mouse_pos:
                start_scr = self.to_screen(self.current_ruler_start)
                
                # Logic snap cho ruler
                mouse_x, mouse_y = self.mouse_pos
                snap_scr = self.to_screen(self.snapped_point)
                mouse_scr = self.to_screen(self.mouse_pos)

                if snap_scr: # Ưu tiên snap vào object
                    end_point = snap_scr
                    painter.setPen(QPen(QColor("yellow"), 2))
                    painter.drawEllipse(snap_scr, 8, 8)
                else:
                    end_point = mouse_scr
                
                painter.setPen(pen_ruler)
                painter.drawLine(start_scr, end_point)

    def mouseMoveEvent(self, event):
        if self.image is None: return
        img_pos = self.transform_pos(event.pos())
        self.mouse_pos = img_pos

        if self.is_input:
            if self.mode == "PAINT" and (event.buttons() & Qt.MouseButton.LeftButton):
                # Logic Vẽ Tay
                if self.last_draw_pos:
                    # Xử lý Snap khi vẽ (nếu bật)
                    curr_x, curr_y = img_pos
                    if self.snap_to_grid:
                        curr_x, curr_y = self.apply_snap(curr_x, curr_y)
                    
                    current_snap_pos = (curr_x, curr_y)
                    self.paint_on_canvas(self.last_draw_pos, current_snap_pos)
                    self.last_draw_pos = current_snap_pos # Cập nhật điểm cuối
                
            elif self.mode == "BOX" and self.box_start:
                self.box_current = img_pos
                self.update()
        else:
            if self.mode == "RULER" and self.contour is not None:
                self.snapped_point = GeometryUtils.get_closest_point(img_pos, self.contour)
                self.update()

    def mousePressEvent(self, event):
        if self.image is None: return
        img_pos = self.transform_pos(event.pos())

        if self.is_input:
            if self.mode == "POINT":
                self.request_mask_point.emit(img_pos[0], img_pos[1])
            elif self.mode == "BOX":
                self.box_start = img_pos
                self.box_current = img_pos
            elif self.mode == "PAINT":
                # Bắt đầu nét vẽ
                start_x, start_y = img_pos
                if self.snap_to_grid:
                    start_x, start_y = self.apply_snap(start_x, start_y)
                self.last_draw_pos = (start_x, start_y)
                # Vẽ 1 chấm nếu click đơn
                self.paint_on_canvas(self.last_draw_pos, self.last_draw_pos)

        else:
            # Logic Thước đo (Output)
            if self.mode == "RULER":
                target = self.snapped_point if self.snapped_point else img_pos
                if event.button() == Qt.MouseButton.RightButton:
                    if self.measurements:
                        self.measurements.pop()
                        self.update()
                    self.current_ruler_start = None
                    return
                if self.current_ruler_start is None:
                    self.current_ruler_start = target
                else:
                    self.measurements.append((self.current_ruler_start, target))
                    dist = GeometryUtils.distance(self.current_ruler_start, target)
                    self.ruler_updated.emit(dist)
                    self.current_ruler_start = None 
                self.update()

    def mouseReleaseEvent(self, event):
        if self.is_input:
            if self.mode == "BOX" and self.box_start:
                end_pos = self.transform_pos(event.pos())
                x1, x2 = sorted([self.box_start[0], end_pos[0]])
                y1, y2 = sorted([self.box_start[1], end_pos[1]])
                if (x2 - x1) > 5 and (y2 - y1) > 5:
                    self.request_mask_box.emit(x1, y1, x2, y2)
                self.box_start = None
                self.box_current = None
                self.update()
            elif self.mode == "PAINT":
                self.last_draw_pos = None # Kết thúc nét vẽ