'use client';

import { useState, useEffect } from 'react';
import { getNextCard, reviewCard, type CardResponse, type ReviewResponse } from '@/lib/api';
import { useSessionStore } from '@/store/sessionStore';
import { FlipCard } from '@/components/cards/FlipCard';
import { SAMSlider } from '@/components/state/SAMSlider';
import { BookOpen, Loader2, Sparkles } from 'lucide-react';

export default function LearnPage() {
  const [card, setCard] = useState<CardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [justReviewed, setJustReviewed] = useState(false);
  const { sessionId, incrementCardsReviewed } = useSessionStore();

  useEffect(() => {
    fetchNextCard();
  }, []);

  const fetchNextCard = async () => {
    setLoading(true);
    try {
      const nextCard = await getNextCard();
      setCard(nextCard);
    } catch (error) {
      console.error('Failed to fetch next card:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (quality: number) => {
    if (!card || !sessionId) return;

    setJustReviewed(true);
    try {
      await reviewCard(card.id, quality, sessionId);
      incrementCardsReviewed();
    } catch (error) {
      console.error('Failed to review card:', error);
    }

    setTimeout(() => {
      setJustReviewed(false);
      fetchNextCard();
    }, 800);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
        <p className="text-gray-500">正在加载学习卡片...</p>
      </div>
    );
  }

  if (!card) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <BookOpen className="w-16 h-16 text-gray-300 mb-4" />
        <p className="text-gray-500">暂无学习卡片</p>
        <p className="text-gray-400 text-sm mt-1">请先添加学习内容</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-800">卡片学习</h1>
        <p className="text-gray-500 mt-1">点击卡片翻转查看答案，然后评估掌握程度</p>
      </div>

      <div className="mb-8">
        <FlipCard card={card} onReview={handleReview} />
      </div>

      {justReviewed && (
        <div className="text-center mb-6 animate-fade-in">
          <Sparkles className="w-8 h-8 text-green-500 mx-auto mb-2" />
          <p className="text-green-600 font-medium">复习成功！继续保持~</p>
        </div>
      )}

      <div className="mt-8">
        <h3 className="text-sm font-medium text-gray-600 mb-3 text-center">自我评估状态</h3>
        <SAMSlider />
      </div>
    </div>
  );
}