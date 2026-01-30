import React from 'react';

const Toolbar = ({ activeTool, setTool, showGrid, setShowGrid }) => {
  return (
    <div className="toolbar-sidebar">
      <div className="tool-group">
        <button 
          className={`tool-btn ${activeTool === 'hand' ? 'active' : ''}`}
          onClick={() => setTool('hand')}
          title="Hand Tool (H) - Kéo và Di chuyển"
        >
          🖐️ Pan
        </button>
        
        <button 
          className={`tool-btn ${activeTool === 'box' ? 'active' : ''}`}
          onClick={() => setTool('box')}
          title="Box Tool (B) - Vẽ vùng chọn AI"
        >
          🎯 AI Box
        </button>

        {/* Mở rộng sau này: Brush, Eraser, Ruler */}
      </div>

      <div className="tool-group divider">
        <button 
          className={`tool-btn ${showGrid ? 'active-secondary' : ''}`}
          onClick={() => setShowGrid(!showGrid)}
          title="Bật/Tắt Lưới"
        >
          Grid {showGrid ? 'ON' : 'OFF'}
        </button>
      </div>
    </div>
  );
};

export default Toolbar;