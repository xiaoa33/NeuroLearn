'use client';

import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import { getChapterName } from '@/lib/utils';

interface RadarChartProps {
  chapterStrengths: Record<number, number>;
}

export function RadarChartComponent({ chapterStrengths }: RadarChartProps) {
  const data = Object.entries(chapterStrengths)
    .map(([chapter, strength]) => ({
      subject: getChapterName(Number(chapter)),
      chapter: Number(chapter),
      strength: strength * 100,
      fullMark: 100,
    }))
    .sort((a, b) => a.chapter - b.chapter);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      <h3 className="font-semibold text-gray-800 mb-4">章节掌握度</h3>
      
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data}>
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: '#6b7280', fontSize: 11 }}
            />
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 100]} 
              tick={{ fill: '#9ca3af', fontSize: 10 }}
              tickCount={5}
            />
            <Tooltip 
              formatter={(value: number) => [`${value.toFixed(1)}%`, '掌握度']}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
            />
            <Radar
              name="掌握度"
              dataKey="strength"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}