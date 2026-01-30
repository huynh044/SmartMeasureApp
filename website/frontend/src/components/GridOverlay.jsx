import React from 'react';
import { Group, Line } from 'react-konva';

const GridOverlay = ({ width, height, size = 50, visible }) => {
  if (!visible) return null;

  const lines = [];
  
  // Vẽ các đường dọc
  for (let i = 0; i <= width; i += size) {
    lines.push(
      <Line
        key={`v-${i}`}
        points={[i, 0, i, height]}
        stroke="rgba(255, 255, 255, 0.2)"
        strokeWidth={1}
        listening={false} // QUAN TRỌNG: Chuột xuyên qua lưới
      />
    );
  }

  // Vẽ các đường ngang
  for (let j = 0; j <= height; j += size) {
    lines.push(
      <Line
        key={`h-${j}`}
        points={[0, j, width, j]}
        stroke="rgba(255, 255, 255, 0.2)"
        strokeWidth={1}
        listening={false}
      />
    );
  }

  return <Group>{lines}</Group>;
};

export default GridOverlay;