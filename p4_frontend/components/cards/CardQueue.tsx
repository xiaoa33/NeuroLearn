'use client';

import type { CardResponse } from '@/lib/api';
import { getChapterName, getMemoryStrengthColor, formatTimeRemaining } from '@/lib/utils';
import { Clock, Brain } from 'lucide-react';

interface CardQueueProps {
  cards: CardResponse[];
  onSelectCard: (card: CardResponse) => void;
}

export function CardQueue({ cards, onSelectCard }: CardQueueProps) {
  return (
    <div className="space-y-3">
      {cards.length === 0 ? (
        <div className="text-center py-12">
          <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">暂无待复习卡片</p>
          <p className="text-gray-400 text-sm mt-1">去学习页面开始新的学习吧</p>
        </div>
      ) : (
        cards.map((card) => {
          const strengthColor = getMemoryStrengthColor(card.memory_strength);
          
          return (
            <div
              key={card.id}
              onClick={() => onSelectCard(card)}
              className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 hover:shadow-md hover:border-primary-200 transition-all duration-200 cursor-pointer group"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-0.5 bg-primary-100 text-primary-600 text-xs rounded-full">
                      {getChapterName(card.chapter)}
                    </span>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: card.difficulty }).map((_, i) => (
                        <span key={i} className="text-xs">★</span>
                      ))}
                    </div>
                  </div>
                  <h3 className="font-medium text-gray-800 group-hover:text-primary-600 transition-colors">
                    {card.front}
                  </h3>
                </div>
                
                <div className="text-right">
                  <div className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatTimeRemaining(card.next_review_at)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all duration-300"
                        style={{ width: `${card.memory_strength * 100}%`, backgroundColor: strengthColor }}
                      />
                    </div>
                    <span 
                      className="text-xs font-medium"
                      style={{ color: strengthColor }}
                    >
                      {(card.memory_strength * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}