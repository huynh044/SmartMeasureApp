import os
import sys
import cv2
import numpy as np
import torch
from mobile_sam import sam_model_registry, SamPredictor

class AIProcessor:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"⚙️ AI Engine: {self.device.upper()}")

        if getattr(sys, 'frozen', False):
            # Nếu đang chạy trong file .exe (PyInstaller)
            base_path = sys._MEIPASS
        else:
            # Nếu đang chạy code Python bình thường
            base_path = os.path.abspath(".")
            
        # Nối đường dẫn chuẩn
        model_path = os.path.join(base_path, "assets", "models", "mobile_sam.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Thiếu model tại: {model_path}")

        try:
            self.sam = sam_model_registry["vit_t"](checkpoint=model_path)
            self.sam.to(device=self.device)
            self.sam.eval()
            self.predictor = SamPredictor(self.sam)
            self.is_image_set = False
        except Exception as e:
            raise RuntimeError(f"❌ Lỗi load model: {str(e)}")

    def set_image(self, image_cv2):
        image_rgb = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
        self.predictor.set_image(image_rgb)
        self.is_image_set = True

    def predict_click(self, x, y):
        """Chọn bằng điểm"""
        if not self.is_image_set: return None
        input_point = np.array([[x, y]])
        input_label = np.array([1])
        masks, scores, _ = self.predictor.predict(point_coords=input_point, point_labels=input_label, multimask_output=True)
        return (masks[np.argmax(scores)] * 255).astype(np.uint8)

    def predict_box(self, x1, y1, x2, y2):
        """Chọn bằng hình chữ nhật (Box Prompt)"""
        if not self.is_image_set: return None
        # MobileSAM yêu cầu box dạng [x1, y1, x2, y2]
        input_box = np.array([x1, y1, x2, y2])
        
        masks, scores, _ = self.predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_box[None, :], # Thêm chiều batch
            multimask_output=True
        )
        return (masks[np.argmax(scores)] * 255).astype(np.uint8)