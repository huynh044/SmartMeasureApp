import cv2
import numpy as np

class GeometryUtils:
    @staticmethod
    def get_contour(mask):
        """Tìm đường viền lớn nhất từ Mask"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None
        # Lấy contour có diện tích lớn nhất (bỏ qua nhiễu)
        c = max(contours, key=cv2.contourArea)
        return c

    @staticmethod
    def smooth_contour(contour, epsilon_factor=0.002):
        """Làm mượt đường viền để bớt răng cưa"""
        peri = cv2.arcLength(contour, True)
        epsilon = epsilon_factor * peri
        return cv2.approxPolyDP(contour, epsilon, True)

    @staticmethod
    def compute_metrics(contour, scale_factor):
        """
        Tính Diện tích & Chu vi thực tế.
        scale_factor: đơn vị cm/pixel
        """
        # 1. Tính toán trên Pixel
        area_px = cv2.contourArea(contour)
        perimeter_px = cv2.arcLength(contour, True)

        # 2. Quy đổi sang CM
        # Diện tích = pixel * scale^2
        real_area = area_px * (scale_factor ** 2)
        # Chu vi = pixel * scale
        real_perimeter = perimeter_px * scale_factor

        return real_area, real_perimeter

    @staticmethod
    def distance(p1, p2):
        """Tính khoảng cách giữa 2 điểm (x1,y1) và (x2,y2)"""
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    
    @staticmethod
    def get_closest_point(point, contour, threshold=20):
        """
        Tìm điểm trên đường viền gần chuột nhất (Tính năng Bắt điểm / Snapping)
        point: (x, y) chuột
        contour: đường viền
        threshold: khoảng cách tối đa để bắt điểm
        """
        if contour is None: return None
        
        min_dist = float('inf')
        closest_pt = None
        
        # Duyệt qua các điểm trên contour
        # (Lưu ý: Có thể tối ưu hơn bằng KDTree nếu hình quá lớn, nhưng v1 cứ for loop)
        for pt in contour:
            px, py = pt[0]
            dist = (px - point[0])**2 + (py - point[1])**2
            if dist < min_dist:
                min_dist = dist
                closest_pt = (px, py)
        
        # Nếu nằm trong bán kính hút (threshold^2 vì ta chưa căn bậc 2 dist)
        if min_dist < threshold**2:
            return closest_pt
        return None