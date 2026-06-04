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
      <p className="text-xs text-gray-400 mb-3 text-center">拖动滑条告诉系统你现在的状态，帮助它为你调整学习节奏</p>
      <div className="space-y-5">
        {/* 效价：心情好坏 */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <div className="flex items-center gap-1">
              <span className="text-sm font-medium text-gray-700">心情</span>
              <span className="text-xs text-gray-400 ml-1">（效价）</span>
            </div>
            <span className="text-xs text-gray-400">{samValence.toFixed(1)}</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-base">😞</span>
            <input
              type="range"
              min="0"
              max="10"
              step="0.1"
              value={samValence}
              onChange={handleValenceChange}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
            <span className="text-base">😊</span>
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1 px-7">
            <span>心情低落</span>
            <span>心情愉快</span>
          </div>
        </div>

        {/* 唤醒：精力状态 */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <div className="flex items-center gap-1">
              <span className="text-sm font-medium text-gray-700">精力</span>
              <span className="text-xs text-gray-400 ml-1">（唤醒度）</span>
            </div>
            <span className="text-xs text-gray-400">{samArousal.toFixed(1)}</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-base">😴</span>
            <input
              type="range"
              min="0"
              max="10"
              step="0.1"
              value={samArousal}
              onChange={handleArousalChange}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-500"
            />
            <span className="text-base">⚡</span>
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1 px-7">
            <span>困倦疲惫</span>
            <span>精力充沛</span>
          </div>
        </div>
      </div>
    </div>
  );
}