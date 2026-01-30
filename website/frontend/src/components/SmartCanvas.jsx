import React, { useState, useRef, useEffect } from 'react';
import { Stage, Layer, Image as KonvaImage, Rect } from 'react-konva';
import useImage from 'use-image';
import GridOverlay from './GridOverlay';
import { predictMask } from '../api/client';

const SmartCanvas = ({ 
  file, 
  image, // Lưu ý: props bây giờ nhận image object (đã load) chứ ko chỉ file
  activeTool, 
  showGrid, 
  gridConfig, // <--- Props mới
  onProcessing 
}) => {
  // 1. Load ảnh & Mask
  const [imageBitmap] = useImage(file ? URL.createObjectURL(file) : null);
  const [maskSrc, setMaskSrc] = useState(null);
  const [maskBitmap] = useImage(maskSrc);

  // 2. Viewport State (Zoom & Pan)
  const [stageScale, setStageScale] = useState(1);
  const [stagePos, setStagePos] = useState({ x: 0, y: 0 });

  // 3. Drawing State (Vẽ Box)
  const [isDrawing, setIsDrawing] = useState(false);
  const [newBox, setNewBox] = useState(null); // {x, y, w, h}

  const stageRef = useRef(null);

  // --- LOGIC 1: Reset khi có ảnh mới ---
  useEffect(() => {
    if (imageBitmap) {
      // Fit ảnh vào giữa màn hình
      const padding = 50;
      const availableW = window.innerWidth - 80; // Trừ sidebar
      const availableH = window.innerHeight - 60; // Trừ header
      
      const scale = Math.min(
        availableW / imageBitmap.width,
        availableH / imageBitmap.height
      );
      
      setStageScale(scale);
      setStagePos({
        x: (availableW - imageBitmap.width * scale) / 2 + 80, // Offset sidebar
        y: (availableH - imageBitmap.height * scale) / 2
      });
      setMaskSrc(null);
      setNewBox(null);
    }
  }, [imageBitmap]);

  // --- LOGIC 2: Zoom mượt bằng lăn chuột (Google Maps style) ---
  const handleWheel = (e) => {
    e.evt.preventDefault();
    const stage = stageRef.current;
    const oldScale = stage.scaleX();

    const pointer = stage.getPointerPosition();
    const mousePointTo = {
      x: (pointer.x - stage.x()) / oldScale,
      y: (pointer.y - stage.y()) / oldScale,
    };

    const scaleBy = 1.1;
    const newScale = e.evt.deltaY < 0 ? oldScale * scaleBy : oldScale / scaleBy;

    // Giới hạn zoom
    if (newScale < 0.1 || newScale > 10) return;

    setStageScale(newScale);
    setStagePos({
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale,
    });
  };

  // --- LOGIC 3: Xử lý Vẽ Box (Chỉ khi Tool == 'box') ---
  const handleMouseDown = (e) => {
    if (activeTool !== 'box' || !imageBitmap) return;

    const stage = e.target.getStage();
    const pos = stage.getRelativePointerPosition(); // Tọa độ so với ảnh gốc
    
    setIsDrawing(true);
    setNewBox({ x: pos.x, y: pos.y, w: 0, h: 0 });
    setMaskSrc(null); // Xóa mask cũ
  };

  const handleMouseMove = (e) => {
    if (!isDrawing) return;
    
    const stage = e.target.getStage();
    const pos = stage.getRelativePointerPosition();
    
    setNewBox((prev) => ({
      ...prev,
      w: pos.x - prev.x,
      h: pos.y - prev.y,
    }));
  };

  const handleMouseUp = async () => {
    if (!isDrawing) return;
    setIsDrawing(false);

    // Tính toán tọa độ chuẩn (bất kể kéo từ hướng nào)
    if (newBox && Math.abs(newBox.w) > 5 && Math.abs(newBox.h) > 5) {
      const x1 = Math.min(newBox.x, newBox.x + newBox.w);
      const y1 = Math.min(newBox.y, newBox.y + newBox.h);
      const x2 = Math.max(newBox.x, newBox.x + newBox.w);
      const y2 = Math.max(newBox.y, newBox.y + newBox.h);

      // GỌI API
      onProcessing(true);
      try {
        const coords = [Math.floor(x1), Math.floor(y1), Math.floor(x2), Math.floor(y2)];
        const result = await predictMask(file, coords);
        setMaskSrc(`data:image/png;base64,${result.mask}`);
      } catch (err) {
        console.error(err);
        alert("Lỗi AI: " + err.message);
      } finally {
        onProcessing(false);
        setNewBox(null);
      }
    }
  };

  if (!imageBitmap) return <div className="placeholder">Kéo thả hoặc chọn ảnh để bắt đầu</div>;

  return (
    <div className={`canvas-wrapper cursor-${activeTool}`}>
      <Stage
        width={window.innerWidth}
        height={window.innerHeight}
        onWheel={handleWheel}
        scaleX={stageScale}
        scaleY={stageScale}
        x={stagePos.x}
        y={stagePos.y}
        draggable={activeTool === 'hand'} // CHỈ KÉO ĐƯỢC KHI Ở CHẾ ĐỘ HAND
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        ref={stageRef}
      >
        <Layer>
          {/* 1. Ảnh Gốc */}
          <KonvaImage image={image} />

          {/* 2. Mask AI (Phủ đè lên ảnh) */}
          {maskBitmap && (
            <KonvaImage image={maskBitmap} opacity={0.6} listening={false} />
          )}

          {/* 3. Lưới (Grid Overlay) */}
          <GridOverlay 
          width={image.width} 
          height={image.height} 
          visible={showGrid} 
          size={gridConfig.size}       // <-- Lấy từ props
          stroke={gridConfig.color}    // <-- Lấy từ props
          opacity={gridConfig.opacity} // <-- Lấy từ props
        />

          {/* 4. Box đang vẽ */}
          {newBox && (
            <Rect
              x={newBox.x}
              y={newBox.y}
              width={newBox.w}
              height={newBox.h}
              stroke="#00ff00"
              strokeWidth={2 / stageScale} // Nét vẽ luôn mảnh dù zoom to
              dash={[5, 5]}
            />
          )}
        </Layer>
      </Stage>
    </div>
  );
};

export default SmartCanvas;