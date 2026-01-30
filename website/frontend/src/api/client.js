import axios from 'axios';

// Đổi thành IP máy chủ nếu deploy, hiện tại để localhost
const API_URL = 'http://localhost:8000';

export const predictMask = async (imageFile, boxCoords) => {
    // boxCoords dạng mảng: [x1, y1, x2, y2]
    
    const formData = new FormData();
    formData.append('file', imageFile);
    // Backend cần chuỗi JSON, ví dụ: "[100, 200, 300, 400]"
    formData.append('box', JSON.stringify(boxCoords));

    try {
        const response = await axios.post(`${API_URL}/predict`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
        // Trả về object: { mask: "chuỗi_base64_của_ảnh_mask" }
        return response.data;
    } catch (error) {
        console.error("Lỗi gọi AI:", error);
        throw error;
    }
};