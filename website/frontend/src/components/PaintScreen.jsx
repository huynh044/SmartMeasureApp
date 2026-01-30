import React, { useState } from 'react';
import Toolbar from './Toolbar'; // Dùng lại toolbar cũ của bạn
import SmartCanvas from './SmartCanvas';
import PropertiesPanel from './PropertiesPanel';

const PaintScreen = ({ file, image, gridConfig, setGridConfig }) => {
  const [activeTool, setActiveTool] = useState('hand');
  const [showGrid, setShowGrid] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  // Nếu chưa có ảnh, hiện Placeholder
  if (!image) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-[#121212] text-gray-500">
        <div className="text-6xl mb-4">🎨</div>
        <p className="text-xl">Chưa có ảnh nào.</p>
        <p className="text-sm mt-2">Vui lòng quay lại tab <b>Input</b> để tải ảnh lên.</p>
        
        {/* Vẫn cho chỉnh Grid chơi */}
        <div className="absolute right-0 top-0 h-full border-l border-[#333]">
           <PropertiesPanel gridConfig={gridConfig} setGridConfig={setGridConfig} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full h-full bg-[#1e1e1e] overflow-hidden">
      {/* 1. Toolbar bên trái */}
      <Toolbar 
        activeTool={activeTool} 
        setTool={setActiveTool} 
        showGrid={showGrid}
        setShowGrid={setShowGrid}
      />

      {/* 2. Canvas ở giữa */}
      <div className="flex-1 bg-[#000] relative overflow-hidden">
        <SmartCanvas 
          file={file}
          image={image}
          activeTool={activeTool}
          showGrid={showGrid}
          gridConfig={gridConfig} // Truyền Grid Config vào đây
          onProcessing={setIsProcessing}
        />
        {isProcessing && (
           <div className="absolute top-4 right-4 bg-[#0078d4] text-white px-4 py-2 rounded shadow animate-pulse">
             ⚡ Đang xử lý AI...
           </div>
        )}
      </div>

      {/* 3. Properties bên phải */}
      <PropertiesPanel gridConfig={gridConfig} setGridConfig={setGridConfig} />
    </div>
  );
};

export default PaintScreen;