'use client';

import { useState, useEffect } from 'react';
import { getNextCard, type CardResponse } from '@/lib/api';
import { CardQueue } from '@/components/cards/CardQueue';
import { RefreshCw, Clock, Filter, ChevronRight } from 'lucide-react';

export default function ReviewPage() {
  const [cards, setCards] = useState<CardResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'due' | 'weak'>('all');

  useEffect(() => {
    fetchDueCards();
  }, [filter]);

  const fetchDueCards = async () => {
    setLoading(true);
    try {
      const allCards: CardResponse[] = [];
      let hasMore = true;
      let count = 0;

      while (hasMore && count < 50) {
        try {
          const card = await getNextCard();
          if (card) {
            allCards.push(card);
            count++;
          } else {
            hasMore = false;
          }
        } catch {
          hasMore = false;
        }
      }

      let filteredCards = allCards;
      if (filter === 'due') {
        filteredCards = allCards.filter(c => new Date(c.next_review_at) <= new Date());
      } else if (filter === 'weak') {
        filteredCards = allCards.filter(c => c.memory_strength < 0.5);
      }

      setCards(filteredCards);
    } catch (error) {
      console.error('Failed to fetch due cards:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCard = (card: CardResponse) => {
    window.location.href = `/learn?card=${card.id}`;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <RefreshCw className="w-12 h-12 text-primary-500 animate-spin mb-4" />
        <p className="text-gray-500">正在加载待复习卡片...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">复习队列</h1>
          <p className="text-gray-500 mt-1">查看和管理需要复习的卡片</p>
        </div>
        <button
          onClick={fetchDueCards}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          刷新
        </button>
      </div>

      <div className="flex items-center gap-2 mb-6">
        <Filter className="w-4 h-4 text-gray-400" />
        {[
          { value: 'all', label: '全部' },
          { value: 'due', label: '已到期' },
          { value: 'weak', label: '记忆较弱' },
        ].map(item => (
          <button
            key={item.value}
            onClick={() => setFilter(item.value as typeof filter)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              filter === item.value
                ? 'bg-primary-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-gray-600">
            <Clock className="w-5 h-5" />
            <span className="font-medium">待复习卡片</span>
            <span className="px-2 py-0.5 bg-primary-100 text-primary-600 rounded-full text-sm">
              {cards.length} 张
            </span>
          </div>
        </div>

        <CardQueue cards={cards} onSelectCard={handleSelectCard} />

        {cards.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-100">
            <button
              onClick={() => window.location.href = '/learn'}
              className="w-full py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg font-medium hover:from-primary-600 hover:to-primary-700 transition-all flex items-center justify-center gap-2"
            >
              开始复习
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}