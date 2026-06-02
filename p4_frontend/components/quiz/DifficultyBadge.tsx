'use client';

import { useState, useEffect } from 'react';
import { getDifficultyLabel, getDifficultyColor } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface DifficultyBadgeProps {
  difficulty: number;
  previousDifficulty?: number;
}

export function DifficultyBadge({ difficulty, previousDifficulty }: DifficultyBadgeProps) {
  const [showBubble, setShowBubble] = useState(false);
  const [bubbleMessage, setBubbleMessage] = useState('');

  const color = getDifficultyColor(difficulty);
  const label = getDifficultyLabel(difficulty);

  useEffect(() => {
    if (previousDifficulty !== undefined && previousDifficulty !== difficulty) {
      if (difficulty > previousDifficulty) {
        setBubbleMessage('感觉不错，提升难度~');
      } else {
        setBubbleMessage('感觉有些困难，降低难度~');
      }
      setShowBubble(true);
      setTimeout(() => setShowBubble(false), 3000);
    }
  }, [difficulty, previousDifficulty]);

  const getTrendIcon = () => {
    if (previousDifficulty === undefined) return null;
    if (difficulty > previousDifficulty) return <TrendingUp className="w-4 h-4" />;
    if (difficulty < previousDifficulty) return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  return (
    <div className="relative inline-flex items-center gap-2">
      <div 
        className="px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 transition-all duration-300"
        style={{ 
          backgroundColor: `${color}15`,
          color: color,
          border: `1px solid ${color}30`
        }}
      >
        {getTrendIcon()}
        <span>{label}</span>
      </div>
      
      {showBubble && (
        <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-sm px-3 py-2 rounded-lg animate-fade-in">
          {bubbleMessage}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-full border-4 border-transparent border-t-gray-800" />
        </div>
      )}
    </div>
  );
}