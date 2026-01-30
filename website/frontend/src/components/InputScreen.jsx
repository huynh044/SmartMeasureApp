import React from 'react';
import { Upload } from 'lucide-react';

const InputScreen = ({ onFileSelect }) => {
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-[#121212] text-white">
      <div className="text-center space-y-6 max-w-lg p-10 border-2 border-dashed border-[#333] rounded-2xl hover:border-[#0078d4] transition-colors bg-[#1e1e1e]">
        <div className="mx-auto w-20 h-20 bg-[#2b2b2b] rounded-full flex items-center justify-center text-[#0078d4]">
          <Upload size={40} />
        </div>
        
        <div>
          <h2 className="text-3xl font-bold mb-2">Bắt đầu Dự án mới</h2>
          <p className="text-gray-400">Kéo thả ảnh vào đây hoặc bấm nút bên dưới</p>
        </div>

        <div className="relative">
          <input 
            type="file" 
            accept="image/*" 
            onChange={handleFileChange} 
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />
          <button className="bg-[#0078d4] hover:bg-[#0063b1] text-white px-8 py-3 rounded-lg font-bold transition-all">
            Chọn Ảnh từ Máy
          </button>
        </div>
      </div>
    </div>
  );
};

export default InputScreen;