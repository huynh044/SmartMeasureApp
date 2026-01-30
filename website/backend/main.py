# website/backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import base64
import json

# Import class AI cũ của bạn
from engine.ai_processor import AIProcessor 

app = FastAPI()

# Cấu hình CORS (Cho phép Frontend React gọi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo AI (Load model 1 lần duy nhất khi bật server)
try:
    ai_processor = AIProcessor()
    print("AI Model loaded successfully!")
except Exception as e:
    print(f"Error loading AI: {e}")
    ai_processor = None

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    box: str = Form(...) # Nhận chuỗi "[x1, y1, x2, y2]"
):
    if ai_processor is None:
        return {"error": "AI not loaded"}

    # 1. Đọc ảnh
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Set ảnh cho AI
    ai_processor.set_image(image)

    # 3. Parse tọa độ Box từ client gửi lên
    # Client gửi dạng string "[10, 20, 100, 200]" -> convert sang list
    box_coords = json.loads(box) 
    x1, y1, x2, y2 = box_coords

    # 4. Dự đoán
    mask = ai_processor.predict_box(x1, y1, x2, y2)

    # 5. Trả về kết quả (Mask dạng base64 để frontend vẽ)
    mask_img = (mask * 255).astype(np.uint8)
    _, buffer = cv2.imencode('.png', mask_img)
    mask_base64 = base64.b64encode(buffer).decode('utf-8')

    return {"mask": mask_base64}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)