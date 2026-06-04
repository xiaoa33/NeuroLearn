'use client';

import { useEffect } from 'react';
import { useSessionStore } from '@/store/sessionStore';
import { formatDuration } from '@/lib/utils';
import { StateIndicator } from '@/components/state/StateIndicator';

export function TopBar() {
  const { duration, incrementDuration, currentState, stateSuggestion } = useSessionStore();

  useEffect(() => {
    const interval = setInterval(() => {
      incrementDuration();
    }, 1000);

    return () => clearInterval(interval);
  }, [incrementDuration]);

  return (
    <header className="fixed top-0 left-16 right-0 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 z-40">
      <div className="flex items-center gap-3 min-w-0">
        <h1 className="text-xl font-semibold text-gray-800 flex-shrink-0">NeuroLearn</h1>
        <StateIndicator />
        {currentState !== 'flow' && stateSuggestion && (
          <span
            key={stateSuggestion}
            className="text-xs text-gray-400 truncate max-w-xs animate-fade-in hidden md:block"
          >
            {stateSuggestion}
          </span>
        )}
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-gray-600">
          <span className="text-sm font-medium">学习时长</span>
          <span className="text-lg font-mono font-semibold text-primary-600">
            {formatDuration(duration)}
          </span>
        </div>
        
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
          <span className="text-white text-sm font-medium">N</span>
        </div>
      </div>
    </header>
  );
}