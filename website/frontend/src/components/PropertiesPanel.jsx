import React from 'react';

const PropertiesPanel = ({ gridConfig, setGridConfig }) => {
  const handleChange = (key, value) => {
    setGridConfig({ ...gridConfig, [key]: value });
  };

  return (
    <div className="w-72 h-full bg-[#1e1e1e] border-l border-[#333] p-4 text-white overflow-y-auto">
      <h3 className="font-bold text-lg mb-4 text-[#0078d4]">Thuộc tính</h3>
      
      {/* GRID SETTINGS */}
      <div className="mb-6 p-3 bg-[#2b2b2b] rounded-lg">
        <h4 className="text-sm font-bold text-gray-400 mb-3 uppercase">Cài đặt Lưới</h4>
        
        {/* Kích thước ô */}
        <div className="mb-4">
          <label className="text-xs text-gray-400 flex justify-between mb-1">
            Kích thước (px) <span>{gridConfig.size}</span>
          </label>
          <input 
            type="range" min="10" max="200" step="5"
            value={gridConfig.size}
            onChange={(e) => handleChange('size', parseInt(e.target.value))}
            className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-[#0078d4]"
          />
        </div>

        {/* Độ mờ */}
        <div className="mb-4">
          <label className="text-xs text-gray-400 flex justify-between mb-1">
            Độ mờ <span>{Math.round(gridConfig.opacity * 100)}%</span>
          </label>
          <input 
            type="range" min="0.1" max="1" step="0.1"
            value={gridConfig.opacity}
            onChange={(e) => handleChange('opacity', parseFloat(e.target.value))}
            className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-[#0078d4]"
          />
        </div>

        {/* Màu sắc */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Màu lưới</span>
          <input 
            type="color" 
            value={gridConfig.color}
            onChange={(e) => handleChange('color', e.target.value)}
            className="w-8 h-8 rounded cursor-pointer border-none bg-transparent"
          />
        </div>
      </div>
    </div>
  );
};

export default PropertiesPanel;