'use client';

import { useState, useEffect } from 'react';
import { getDashboardSummary, getCardCurves, type DashboardSummary, type CurveResponse } from '@/lib/api';
import { ForgettingCurve } from '@/components/charts/ForgettingCurve';
import { MemoryHeatmap } from '@/components/charts/MemoryHeatmap';
import { getMemoryStrengthColor, getStateLabel } from '@/lib/utils';
import { Calendar, Flame, Brain, Clock, Target, BookOpen, TrendingUp } from 'lucide-react';

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

      <div className="grid grid-cols-4 gap-4">
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
          <a href="/review" className="text-sm text-primary-600 hover:text-primary-700 mt-3 inline-block">
            去复习 →
          </a>
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
              <p className="text-sm text-gray-500">整体记忆强度</p>
              <p className="text-2xl font-bold mt-1" style={{ color: getMemoryStrengthColor(summary?.overall_memory_strength || 0) }}>
                {((summary?.overall_memory_strength || 0) * 100).toFixed(0)}%
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <Brain className="w-6 h-6 text-blue-500" />
            </div>
          </div>
          <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${(summary?.overall_memory_strength || 0) * 100}%`, backgroundColor: getMemoryStrengthColor(summary?.overall_memory_strength || 0) }}
            />
          </div>
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
          <a href="/quiz" className="text-sm text-primary-600 hover:text-primary-700 mt-3 inline-block">
            去测验 →
          </a>
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
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <div className="w-6 h-6 rounded-full border-2 border-primary-500 flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-primary-500" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-800">复习到期卡片</p>
              <p className="text-sm text-gray-500">提升记忆强度，防止遗忘</p>
            </div>
            <span className="text-sm font-medium text-primary-600">{summary?.due_cards_today || 0} 张</span>
          </div>
          
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <div className="w-6 h-6 rounded-full border-2 border-green-500 flex items-center justify-center">
              <Calendar className="w-4 h-4 text-green-500" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-800">完成每日测验</p>
              <p className="text-sm text-gray-500">检验学习效果，巩固知识</p>
            </div>
            <span className="text-sm font-medium text-green-600">5 题</span>
          </div>
          
          <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <div className="w-6 h-6 rounded-full border-2 border-purple-500 flex items-center justify-center">
              <Brain className="w-4 h-4 text-purple-500" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-gray-800">查看学习洞察</p>
              <p className="text-sm text-gray-500">获取个性化学习建议</p>
            </div>
            <span className="text-sm font-medium text-purple-600">查看 →</span>
          </div>
        </div>
      </div>
    </div>
  );
}