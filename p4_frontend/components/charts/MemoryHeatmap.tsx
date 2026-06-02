'use client';

import { useState } from 'react';
import { getChapterName, getMemoryStrengthColor, getMemoryStrengthLabel } from '@/lib/utils';

interface MemoryHeatmapProps {
  chapterStrengths: Record<number, number>;
  cardCounts?: Record<number, number>;
  nextReviewTimes?: Record<number, string>;
}

export function MemoryHeatmap({ chapterStrengths, cardCounts = {}, nextReviewTimes = {} }: MemoryHeatmapProps) {
  const [hoveredChapter, setHoveredChapter] = useState<number | null>(null);

  const chapters = Object.keys(chapterStrengths)
    .map(Number)
    .sort((a, b) => a - b);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <h3 className="font-semibold text-gray-800 mb-4">章节记忆强度</h3>
      
      <div className="grid grid-cols-4 gap-3">
        {chapters.map(chapter => {
          const strength = chapterStrengths[chapter];
          const color = getMemoryStrengthColor(strength);
          const label = getMemoryStrengthLabel(strength);
          const isHovered = hoveredChapter === chapter;
          
          return (
            <div
              key={chapter}
              className="relative aspect-square rounded-xl cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-md"
              style={{ backgroundColor: `${color}20`, border: `2px solid ${color}` }}
              onMouseEnter={() => setHoveredChapter(chapter)}
              onMouseLeave={() => setHoveredChapter(null)}
            >
              <div className="absolute inset-0 flex flex-col items-center justify-center p-2">
                <span className="text-xs font-medium text-gray-600 mb-1">
                  {getChapterName(chapter)}
                </span>
                <span className="text-xl font-bold" style={{ color }}>
                  {(strength * 100).toFixed(0)}%
                </span>
                <span className="text-xs mt-1" style={{ color }}>
                  {label}
                </span>
              </div>
              
              {isHovered && (
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap z-10">
                  <div className="font-medium mb-1">章节 {chapter}: {getChapterName(chapter)}</div>
                  <div>卡片数: {cardCounts[chapter] || '-'}</div>
                  <div>记忆强度: {(strength * 100).toFixed(1)}%</div>
                  {nextReviewTimes[chapter] && (
                    <div>下次复习: {nextReviewTimes[chapter]}</div>
                  )}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      <div className="flex items-center justify-center gap-6 mt-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#ef444420', border: '2px solid #ef4444' }} />
          <span className="text-xs text-gray-500">薄弱</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#eab30820', border: '2px solid #eab308' }} />
          <span className="text-xs text-gray-500">一般</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: '#22c55e20', border: '2px solid #22c55e' }} />
          <span className="text-xs text-gray-500">牢固</span>
        </div>
      </div>
    </div>
  );
}