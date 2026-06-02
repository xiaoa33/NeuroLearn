'use client';

import { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { CurveResponse, ChapterCurve } from '@/lib/api';
import { getChapterName } from '@/lib/utils';

interface ForgettingCurveProps {
  data: CurveResponse;
}

export function ForgettingCurve({ data }: ForgettingCurveProps) {
  const [selectedChapters, setSelectedChapters] = useState<number[]>(
    data.curves.map(c => c.chapter)
  );

  const allChapters = useMemo(() => data.curves.map(c => c.chapter), [data.curves]);

  const toggleChapter = (chapter: number) => {
    setSelectedChapters(prev => 
      prev.includes(chapter)
        ? prev.filter(c => c !== chapter)
        : [...prev, chapter]
    );
  };

  const filteredCurves = useMemo(() => 
    data.curves.filter(c => selectedChapters.includes(c.chapter)),
    [data.curves, selectedChapters]
  );

  const chartData = useMemo(() => {
    const days = Array.from({ length: 8 }, (_, i) => i);
    return days.map(day => {
      const dayData: Record<string, number> = { day };
      filteredCurves.forEach(curve => {
        const point = curve.points.find(p => p.day === day);
        dayData[`chapter_${curve.chapter}`] = point?.strength ?? 0;
      });
      return dayData;
    });
  }, [filteredCurves]);

  const lines = useMemo(() => 
    filteredCurves.map(curve => ({
      type: 'monotone' as const,
      dataKey: `chapter_${curve.chapter}`,
      name: getChapterName(curve.chapter),
      stroke: getChapterColor(curve.chapter),
      strokeWidth: 2,
      dot: { r: 4 },
      activeDot: { r: 6 },
    })),
    [filteredCurves]
  );

  const weekDays = ['今天', '明天', '后天', '3天后', '4天后', '5天后', '6天后', '7天后'];

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-800">遗忘曲线预测</h3>
        <div className="flex flex-wrap gap-2">
          {allChapters.map(chapter => (
            <button
              key={chapter}
              onClick={() => toggleChapter(chapter)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                selectedChapters.includes(chapter)
                  ? 'bg-primary-100 text-primary-700'
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
              style={selectedChapters.includes(chapter) ? { backgroundColor: `${getChapterColor(chapter)}20`, color: getChapterColor(chapter) } : {}}
            >
              {getChapterName(chapter)}
            </button>
          ))}
        </div>
      </div>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="day" 
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={(day) => weekDays[day] || `第${day}天`}
            />
            <YAxis 
              domain={[0, 1]} 
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            />
            <Tooltip 
              formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, '记忆保留率']}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="threshold" 
              name="复习阈值" 
              stroke="#ef4444" 
              strokeWidth={1} 
              strokeDasharray="5 5"
              isAnimationActive={false}
              hide={true}
            />
            {lines.map((line, index) => (
              <Line key={index} {...line} />
            ))}
            <line 
              x1="0%" y1="70%" x2="100%" y2="70%" 
              stroke="#ef4444" 
              strokeWidth={1} 
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="flex items-center justify-end mt-2 text-xs text-gray-500">
        <span className="flex items-center gap-2">
          <span className="w-3 h-px bg-red-500" style={{ borderTop: '1px dashed #ef4444' }} />
          <span>70% 复习阈值</span>
        </span>
      </div>
    </div>
  );
}

const chapterColors: Record<number, string> = {
  1: '#3b82f6',
  2: '#ef4444',
  3: '#22c55e',
  4: '#eab308',
  5: '#a855f7',
  6: '#ec4899',
  7: '#06b6d4',
  8: '#f97316',
  9: '#8b5cf6',
  10: '#14b8a6',
  11: '#f43f5e',
  12: '#6366f1',
};

function getChapterColor(chapter: number): string {
  return chapterColors[chapter] || '#6b7280';
}