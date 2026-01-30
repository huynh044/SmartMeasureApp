import React from 'react';
import { Upload, Palette, Settings } from 'lucide-react';
import { AppMode } from '../../types';

interface SidebarNavProps {
  currentMode: AppMode;
  setMode: (mode: AppMode) => void;
  hasImage: boolean;
}

export const SidebarNav: React.FC<SidebarNavProps> = ({ currentMode, setMode }) => {
  // Logic cũ: disabled nếu !hasImage -> XÓA BỎ
  // Logic mới: Luôn luôn active
  const navItemClass = (mode: AppMode) => `
    w-12 h-12 flex items-center justify-center rounded-xl transition-all duration-200 mb-4 cursor-pointer
    ${currentMode === mode 
      ? 'bg-[#0078d4] text-white shadow-lg shadow-blue-900/50' 
      : 'text-gray-400 hover:bg-[#3d3d3d] hover:text-white'}
  `;

  return (
    <div className="w-20 h-full bg-[#1e1e1e] border-r border-[#2b2b2b] flex flex-col items-center py-6 z-50">
      {/* Brand Icon */}
      <div className="mb-8 p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg shadow-lg">
        <Settings className="w-6 h-6 text-white" />
      </div>

      {/* Navigation Tabs */}
      <nav className="flex-1 flex flex-col items-center w-full">
        <div 
          className={navItemClass('input')}
          onClick={() => setMode('input')}
          title="Input Mode"
        >
          <Upload className="w-6 h-6" />
        </div>

        <div 
          className={navItemClass('paint')}
          onClick={() => setMode('paint')}
          title="Paint Mode (Workspace)"
        >
          <Palette className="w-6 h-6" />
        </div>
      </nav>
      
      {/* Bottom Actions */}
      <div className="mt-auto flex flex-col items-center gap-4">
        <div className="w-8 h-[1px] bg-[#2b2b2b]" />
        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-gray-700 to-gray-600 flex items-center justify-center text-xs font-bold border border-[#3d3d3d]">
          US
        </div>
      </div>
    </div>
  );
};