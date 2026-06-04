'use client';

import { useState, useEffect } from 'react';
import type { CardResponse } from '@/lib/api';
import { getChapterName, getDifficultyLabel, getDifficultyColor } from '@/lib/utils';
import { Star, RotateCcw } from 'lucide-react';

interface FlipCardProps {
  card: CardResponse;
  onReview: (quality: number) => void;
}

export function FlipCard({ card, onReview }: FlipCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  const [selectedQuality, setSelectedQuality] = useState<number | null>(null);

  useEffect(() => {
    setIsFlipped(false);
    setSelectedQuality(null);
  }, [card.id]);

  const handleFlip = () => {
    if (selectedQuality === null) {
      setIsFlipped(!isFlipped);
    }
  };

  const handleQualitySelect = (quality: number) => {
    setSelectedQuality(quality);
    setTimeout(() => {
      onReview(quality);
    }, 500);
  };

  const difficultyColor = getDifficultyColor(card.difficulty);

  return (
    <div className="w-full max-w-lg mx-auto" style={{ perspective: '1000px' }}>
      <div
        className="relative w-full cursor-pointer"
        onClick={handleFlip}
        style={{
          aspectRatio: '4/3',
          transformStyle: 'preserve-3d',
          transition: 'transform 0.5s',
          transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
        }}
      >
        <div 
          className="card-front absolute inset-0 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl p-6 shadow-xl flex flex-col justify-between"
          style={{ backfaceVisibility: 'hidden' }}
        >
          <div className="flex justify-between items-start">
            <span 
              className="px-3 py-1 rounded-full text-xs font-medium text-white/90 bg-white/20"
            >
              {getChapterName(card.chapter)}
            </span>
            <div className="flex items-center gap-1">
              {Array.from({ length: 3 }).map((_, i) => (
                <Star 
                  key={i} 
                  className={`w-4 h-4 ${i < card.difficulty ? 'text-yellow-300 fill-yellow-300' : 'text-white/30'}`}
                />
              ))}
            </div>
          </div>
          
          <div className="flex-1 flex items-center justify-center">
            <h2 className="text-2xl font-bold text-white text-center leading-relaxed">
              {card.front}
            </h2>
          </div>
          
          <div className="flex justify-center">
            <span className="text-white/70 text-sm">点击翻转查看答案</span>
          </div>
        </div>
        
        <div 
          className="card-back absolute inset-0 bg-white rounded-2xl p-6 shadow-xl flex flex-col justify-between"
          style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
        >
          <div className="flex justify-between items-start">
            <span 
              className="px-3 py-1 rounded-full text-xs font-medium"
              style={{ backgroundColor: `${difficultyColor}15`, color: difficultyColor }}
            >
              {getDifficultyLabel(card.difficulty)}
            </span>
            <RotateCcw className="w-5 h-5 text-gray-400" />
          </div>
          
          <div className="flex-1 flex items-center justify-center">
            <p className="text-xl text-gray-800 text-center leading-relaxed">
              {card.back}
            </p>
          </div>
          
          {card.related_concepts && card.related_concepts.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {card.related_concepts.map((concept, index) => (
                <span 
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                >
                  {concept}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {isFlipped && selectedQuality === null && (
        <div className="mt-6 animate-fade-in">
          <p className="text-center text-gray-500 text-sm mb-4">你掌握得怎么样？</p>
          <div className="flex justify-center gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <button
                key={i}
                onClick={(e) => {
                  e.stopPropagation();
                  handleQualitySelect(i);
                }}
                className={`w-12 h-12 rounded-full font-semibold text-white transition-all duration-200 hover:scale-110 ${
                  i === 0 ? 'bg-red-500' :
                  i === 1 ? 'bg-orange-500' :
                  i === 2 ? 'bg-yellow-500' :
                  i === 3 ? 'bg-blue-500' :
                  i === 4 ? 'bg-green-500' : 'bg-emerald-500'
                }`}
              >
                {i}
              </button>
            ))}
          </div>
          <div className="flex justify-between mt-3 text-xs text-gray-400 px-2">
            <span>完全不会</span>
            <span>完全掌握</span>
          </div>
        </div>
      )}
    </div>
  );
}