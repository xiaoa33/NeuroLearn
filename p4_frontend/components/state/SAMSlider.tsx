'use client';

import { useSessionStore } from '@/store/sessionStore';

export function SAMSlider() {
  const { samValence, samArousal, setSAMScore } = useSessionStore();

  const handleValenceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSAMScore(parseFloat(e.target.value), samArousal);
  };

  const handleArousalChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSAMScore(samValence, parseFloat(e.target.value));
  };

  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <span className="text-lg w-8">😞</span>
          <div className="flex-1">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>效价</span>
              <span>{samValence.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.1"
              value={samValence}
              onChange={handleValenceChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
          </div>
          <span className="text-lg w-8 text-right">😊</span>
        </div>
        
        <div className="flex items-center gap-4">
          <span className="text-lg w-8">😴</span>
          <div className="flex-1">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>唤醒</span>
              <span>{samArousal.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.1"
              value={samArousal}
              onChange={handleArousalChange}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
          </div>
          <span className="text-lg w-8 text-right">⚡</span>
        </div>
      </div>
    </div>
  );
}