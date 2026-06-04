'use client';

import { useState, useEffect } from 'react';
import { getDashboardSummary, getCardCurves, type DashboardSummary, type CurveResponse } from '@/lib/api';
import { ForgettingCurve } from '@/components/charts/ForgettingCurve';
import { MemoryHeatmap } from '@/components/charts/MemoryHeatmap';
import { getStateLabel } from '@/lib/utils';
import Link from 'next/link';
import { Calendar, Flame, Clock, Target, BookOpen, TrendingUp, Brain } from 'lucide-react';

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [curves, setCurves] = useState<CurveResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryData, curvesData] = await Promise.all([
          getDashboardSummary(),
          getCardCurves(),
        ]);
        setSummary(summaryData);
        setCurves(curvesData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">学习仪表盘</h1>
          <p className="text-gray-500 mt-1">查看你的学习进度和记忆状态</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500">今日学习目标</p>
          <p className="text-lg font-semibold text-primary-600">
            复习 {summary?.due_cards_today || 0} 张卡片
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">今日待复习</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">{summary?.due_cards_today || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-orange-100 flex items-center justify-center">
              <Clock className="w-6 h-6 text-orange-500" />
            </div>
          </div>
          <Link href="/review" className="text-sm text-primary-600 hover:text-primary-700 mt-3 inline-block">
            去复习 →
          </Link>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">连续学习</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">{summary?.streak_days || 0} 天</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center">
              <Flame className="w-6 h-6 text-red-500" />
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-3">保持学习习惯，继续加油！</p>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">累计答题</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">{summary?.total_questions_answered || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
              <Target className="w-6 h-6 text-green-500" />
            </div>
          </div>
          <Link href="/quiz" className="text-sm text-primary-600 hover:text-primary-700 mt-3 inline-block">
            去测验 →
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {curves && <ForgettingCurve data={curves} />}
        {summary && <MemoryHeatmap chapterStrengths={summary.chapter_strengths} />}
      </div>

      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary-500" />
          今日任务
        </h3>
        <div className="space-y-3">
          <Link href="/review" className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-primary-50 transition-colors cursor-pointer">
            <div className="w-6 h-6 rounded-full border-2 border-primary-500 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-primary-500" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-800">复习到期卡片</p>
              <p className="text-sm text-gray-500">提升记忆强度，防止遗忘</p>
            </div>
            <span className="text-sm font-medium text-primary-600">{summary?.due_cards_today || 0} 张 →</span>
          </Link>

          <Link href="/quiz" className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-green-50 transition-colors cursor-pointer">
            <div className="w-6 h-6 rounded-full border-2 border-green-500 flex items-center justify-center">
              <Calendar className="w-4 h-4 text-green-500" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-800">完成每日测验</p>
              <p className="text-sm text-gray-500">检验学习效果，巩固知识</p>
            </div>
            <span className="text-sm font-medium text-green-600">去测验 →</span>
          </Link>

          <Link href="/insights" className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-purple-50 transition-colors cursor-pointer">
            <div className="w-6 h-6 rounded-full border-2 border-purple-500 flex items-center justify-center">
              <Brain className="w-4 h-4 text-purple-500" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-800">查看学习洞察</p>
              <p className="text-sm text-gray-500">获取个性化学习建议</p>
            </div>
            <span className="text-sm font-medium text-purple-600">查看 →</span>
          </Link>
        </div>
      </div>
    </div>
  );
}