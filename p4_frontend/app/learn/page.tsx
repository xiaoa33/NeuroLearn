'use client';

import { useState, useEffect, useCallback } from 'react';
import { getNextCard, reviewCard, type CardResponse } from '@/lib/api';
import { useSessionStore } from '@/store/sessionStore';
import { FlipCard } from '@/components/cards/FlipCard';
import { SAMSlider } from '@/components/state/SAMSlider';
import { BookOpen, Loader2, ThumbsUp, RefreshCw, CheckCircle2 } from 'lucide-react';

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

export default function LearnPage() {
  const [card, setCard] = useState<CardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [chapterDone, setChapterDone] = useState(false);
  const [lastQuality, setLastQuality] = useState<number | null>(null);
  const [currentChapter, setCurrentChapter] = useState(1);
  const { sessionId, incrementCardsReviewed } = useSessionStore();

  const fetchNextCard = useCallback(async (chapter: number) => {
    setLoading(true);
    setFetchError(null);
    setChapterDone(false);
    try {
      const nextCard = await getNextCard(chapter, 'learn');
      setCard(nextCard);
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : String(error);
      if (msg.includes('没有找到') || msg.includes('404')) {
        setCard(null);
        setChapterDone(true);
      } else {
        setFetchError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNextCard(currentChapter);
  }, [currentChapter, fetchNextCard]);

  const handleReview = async (quality: number) => {
    if (!card) return;
    setLastQuality(quality);
    try {
      await reviewCard(card.id, quality, sessionId ?? 0);
      incrementCardsReviewed();
    } catch (error) {
      console.error('Failed to review card:', error);
    }
    const delay = quality <= 2 ? 1800 : 900;
    setTimeout(() => {
      setLastQuality(null);
      fetchNextCard(currentChapter);
    }, delay);
  };

  const handleChapterChange = (chapterId: number) => {
    if (chapterId === currentChapter) return;
    setLastQuality(null);
    setCurrentChapter(chapterId);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">卡片学习</h1>
        <p className="text-gray-500 mt-1">点击卡片翻转查看答案，然后评估掌握程度</p>
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
          <p className="text-gray-500">正在加载学习卡片...</p>
        </div>
      ) : fetchError ? (
        <div className="flex flex-col items-center justify-center h-[40vh]">
          <BookOpen className="w-16 h-16 text-red-300 mb-4" />
          <p className="text-gray-500">加载失败，请检查后端服务</p>
          <p className="text-gray-400 text-sm mt-1">{fetchError}</p>
          <button
            onClick={() => fetchNextCard(currentChapter)}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg text-sm"
          >
            重试
          </button>
        </div>
      ) : chapterDone ? (
        <div className="flex flex-col items-center justify-center h-[40vh]">
          <CheckCircle2 className="w-16 h-16 text-green-400 mb-4" />
          <p className="text-xl font-semibold text-gray-700">本章新卡片已全部学完！</p>
          <p className="text-gray-400 text-sm mt-2">切换其他章节继续学习，或前往复习页复习已学内容</p>
        </div>
      ) : card ? (
        <>
          <div className="mb-8">
            <FlipCard card={card} onReview={handleReview} />
          </div>

          {lastQuality !== null && (
            <div className="text-center mb-6 animate-fade-in">
              {lastQuality <= 2 ? (
                <>
                  <RefreshCw className="w-8 h-8 text-amber-500 mx-auto mb-2" />
                  <p className="text-amber-600 font-medium">没关系，再多看看答案，明天继续加油！</p>
                  <p className="text-gray-400 text-sm mt-1">这张卡片将明天再次出现</p>
                </>
              ) : (
                <>
                  <ThumbsUp className="w-8 h-8 text-green-500 mx-auto mb-2" />
                  <p className="text-green-600 font-medium">
                    {lastQuality === 5 ? '完全掌握！记忆间隔已大幅延长 🎉' : '不错！继续保持这个节奏'}
                  </p>
                </>
              )}
            </div>
          )}

          <div className="mt-8">
            <h3 className="text-sm font-medium text-gray-600 mb-3 text-center">自我评估状态</h3>
            <SAMSlider />
          </div>
        </>
      ) : null}
    </div>
  );
}
