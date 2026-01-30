import os
import cv2
import numpy as np
import torch
from mobile_sam import sam_model_registry, SamPredictor

class AIProcessor:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Web Backend AI running on: {self.device}")

        # Đường dẫn tương đối trong Docker/Backend
        # Lưu ý: file này đang ở backend/engine/, model ở backend/assets/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_path, "assets", "models", "mobile_sam.pt")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Không tìm thấy model tại: {model_path}")

        self.sam_checkpoint = model_path
        self.model_type = "vit_t"

        self.mobile_sam = sam_model_registry[self.model_type](checkpoint=self.sam_checkpoint)
        self.mobile_sam.to(device=self.device)
        self.mobile_sam.eval()

        self.predictor = SamPredictor(self.mobile_sam)
        self.current_image = None

    def set_image(self, image_np):
        """
        Input: image_np là ảnh đọc bằng OpenCV (numpy array)
        """
        self.current_image = image_np
        self.predictor.set_image(self.current_image)

    def predict_box(self, x1, y1, x2, y2):
        input_box = np.array([x1, y1, x2, y2])
        masks, _, _ = self.predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_box[None, :],
            multimask_output=False,
        )
        return masks[0]

    # Bỏ hàm predict_click nếu web chưa cần, hoặc sửa tham số x, y thành int thường
    def predict_click(self, x, y):
         # Web gửi lên x, y là số nguyên, không phải QPoint
        input_point = np.array([[x, y]])
        input_label = np.array([1])
        masks, _, _ = self.predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=False,
        )
        return masks[0]