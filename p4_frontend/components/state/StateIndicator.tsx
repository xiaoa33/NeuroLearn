'use client';

import { useSessionStore } from '@/store/sessionStore';
import { getStateLabel, getStateColor } from '@/lib/utils';
import { Activity } from 'lucide-react';

export function StateIndicator() {
  const { currentState } = useSessionStore();
  const label = getStateLabel(currentState);
  const color = getStateColor(currentState);

  return (
    <div 
      className="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-300"
      style={{ 
        backgroundColor: `${color}15`,
        color: color,
        border: `1px solid ${color}30`
      }}
    >
      <Activity className="w-4 h-4" />
      <span>{label}</span>
    </div>
  );
}