'use client';

import { useBehavior } from '@/hooks/useBehavior';

interface BehaviorTrackerProps {
  onStateChange?: (state: string) => void;
}

export function BehaviorTracker({ onStateChange }: BehaviorTrackerProps) {
  const { currentState, stats } = useBehavior();

  if (onStateChange) {
    onStateChange(currentState);
  }

  return (
    <div 
      className="fixed inset-0 pointer-events-none z-50 opacity-0"
      style={{ 
        background: `radial-gradient(circle at center, ${getStateColor(currentState)}05 0%, transparent 70%)` 
      }}
    >
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-gray-900/90 text-white text-xs px-3 py-2 rounded-full flex items-center gap-4">
        <span>状态: {getStateLabel(currentState)}</span>
        <span>正确率: {(stats.correctRate * 100).toFixed(0)}%</span>
        <span>失焦: {stats.unfocusCount}次</span>
      </div>
    </div>
  );
}

function getStateColor(state: string): string {
  const colors: Record<string, string> = {
    flow: '#22c55e',
    anxiety: '#ef4444',
    boredom: '#eab308',
    confusion: '#a855f7',
    fatigue: '#6b7280',
  };
  return colors[state] || '#6b7280';
}

function getStateLabel(state: string): string {
  const labels: Record<string, string> = {
    flow: '心流',
    anxiety: '焦虑',
    boredom: '无聊',
    confusion: '困惑',
    fatigue: '疲劳',
  };
  return labels[state] || state;
}