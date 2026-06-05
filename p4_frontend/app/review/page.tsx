'use client';

import { useState, useEffect, useCallback } from 'react';
import { getNextCard, reviewCard, ApiError, type CardResponse } from '@/lib/api';
import { useSessionStore } from '@/store/sessionStore';
import { FlipCard } from '@/components/cards/FlipCard';
import { SAMSlider } from '@/components/state/SAMSlider';
import { RefreshCw, Loader2, CheckCircle2, BookOpen, ArrowRight } from 'lucide-react';
import Link from 'next/link';

const CHAPTERS = [
  { id: 1, name: '绪论' },
  { id: 2, name: '方法与技术' },
  { id: 3, name: '细胞机制与认知' },
  { id: 4, name: '神经解剖和发展' },
  { id: 7, name: '物体识别' },
  { id: 8, name: '学习与记忆' },
  { id: 9, name: '运动控制' },
  { id: 10, name: '情绪' },
  { id: 11, name: '语言' },
  { id: 12, name: '注意与意识' },
];

export default function ReviewPage() {
  const [card, setCard] = useState<CardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [reviewDone, setReviewDone] = useState(false);
  const [currentChapter, setCurrentChapter] = useState(1);
  const [reviewedCount, setReviewedCount] = useState(0);
  const { sessionId, incrementCardsReviewed } = useSessionStore();

  const fetchNextDueCard = useCallback(async (chapter: number) => {
    setLoading(true);
    setFetchError(null);
    setReviewDone(false);
    try {
      const nextCard = await getNextCard(chapter, 'review');
      setCard(nextCard);
    } catch (error: unknown) {
      if (error instanceof ApiError && error.status === 404) {
        setCard(null);
        setReviewDone(true);
      } else {
        const msg = error instanceof Error ? error.message : String(error);
        setFetchError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setReviewedCount(0);
    fetchNextDueCard(currentChapter);
  }, [currentChapter, fetchNextDueCard]);

  const handleReview = async (quality: number) => {
    if (!card) return;
    try {
      await reviewCard(card.id, quality, sessionId ?? 0);
      incrementCardsReviewed();
      setReviewedCount(prev => prev + 1);
    } catch (error) {
      console.error('Failed to review card:', error);
    }
    const delay = quality <= 2 ? 1800 : 900;
    setTimeout(() => fetchNextDueCard(currentChapter), delay);
  };

  const handleChapterChange = (chapterId: number) => {
    if (chapterId === currentChapter) return;
    setReviewedCount(0);
    setCurrentChapter(chapterId);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">间隔复习</h1>
          <p className="text-gray-500 mt-1">复习 SM-2 算法推送的到期卡片，巩固记忆</p>
        </div>
        {reviewedCount > 0 && (
          <div className="flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-lg">
            <RefreshCw className="w-4 h-4 text-primary-500" />
            <span className="text-sm font-medium text-primary-600">本章已复习 {reviewedCount} 张</span>
          </div>
        )}
      </div>

      {/* 章节选择标签 */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6" style={{ scrollbarWidth: 'thin' }}>
        {CHAPTERS.map(ch => (
          <button
            key={ch.id}
            onClick={() => handleChapterChange(ch.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
              currentChapter === ch.id
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {ch.name}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center h-[40vh]">
          <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
          <p className="text-gray-500">正在加载待复习卡片...</p>
        </div>
      ) : fetchError ? (
        <div className="flex flex-col items-center justify-center h-[40vh]">
          <BookOpen className="w-16 h-16 text-red-300 mb-4" />
          <p className="text-gray-500">加载失败，请检查后端服务</p>
          <p className="text-gray-400 text-sm mt-1">{fetchError}</p>
          <button
            onClick={() => fetchNextDueCard(currentChapter)}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg text-sm"
          >
            重试
          </button>
        </div>
      ) : reviewDone ? (
        <div className="flex flex-col items-center justify-center h-[40vh]">
          <CheckCircle2 className="w-16 h-16 text-green-400 mb-4" />
          <p className="text-xl font-semibold text-gray-700">
            {reviewedCount > 0 ? `本章复习完成！共复习了 ${reviewedCount} 张` : '没有需要复习的内容'}
          </p>
          <p className="text-gray-400 text-sm mt-2 text-center">
            {reviewedCount === 0
              ? '先去学习吧，SM-2 算法会在合适时间安排复习'
              : '记忆已得到强化，下次复习时间由 SM-2 算法自动安排'}
          </p>
          {reviewedCount === 0 && (
            <Link
              href="/learn"
              className="mt-6 flex items-center gap-2 px-6 py-3 bg-primary-500 text-white rounded-xl font-medium hover:bg-primary-600 transition-colors"
            >
              去学习新卡片
              <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </div>
      ) : card ? (
        <>
          <div className="mb-8">
            <FlipCard card={card} onReview={handleReview} />
          </div>
          <div className="mt-8">
            <h3 className="text-sm font-medium text-gray-600 mb-3 text-center">自我评估状态</h3>
            <SAMSlider />
          </div>
        </>
      ) : null}
    </div>
  );
}
