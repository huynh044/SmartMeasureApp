import React, { useState } from 'react';
import SidebarNav from './components/Layout/SidebarNav';
import InputScreen from './components/InputScreen';
import PaintScreen from './components/PaintScreen';
import './App.css'; // File CSS cũ của bạn

function App() {
  // 1. Dữ liệu Global
  const [currentMode, setCurrentMode] = useState('input'); // 'input' | 'paint'
  const [imageObject, setImageObject] = useState(null); // Lưu đối tượng ảnh HTML Image
  const [fileObject, setFileObject] = useState(null);   // Lưu file gốc để gửi API

  // 2. Cấu hình Grid (Lưu ở App để không bị mất khi chuyển tab)
  const [gridConfig, setGridConfig] = useState({
    size: 50,
    color: '#ffffff',
    opacity: 0.3
  });

  // Xử lý khi chọn file từ Input Screen
  const handleFileSelect = (file) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.src = url;
    img.onload = () => {
      setImageObject(img);
      setFileObject(file);
      setCurrentMode('paint'); // Tự động chuyển sang Paint
    };
  };

  return (
    <div className="flex h-screen w-screen bg-[#1e1e1e] overflow-hidden font-sans text-white">
      {/* CỘT 1: Navigation */}
      <SidebarNav currentMode={currentMode} setMode={setCurrentMode} />

      {/* CỘT 2: Main Content */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* MODE 1: INPUT */}
        {currentMode === 'input' && (
          <InputScreen onFileSelect={handleFileSelect} />
        )}

        {/* MODE 2: PAINT (Luôn render được, bên trong tự check ảnh) */}
        {currentMode === 'paint' && (
          <PaintScreen 
            file={fileObject}
            image={imageObject}
            gridConfig={gridConfig}
            setGridConfig={setGridConfig}
          />
        )}

      </main>
    </div>
  );
}

export default App;