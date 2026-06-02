'use client';

import { useState, useEffect } from 'react';
import { getInsightSuggestion, getStateHistory, getDashboardSummary, type InsightResponse, type StateHistoryResponse, type DashboardSummary } from '@/lib/api';
import { RadarChartComponent } from '@/components/charts/RadarChart';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getStateLabel, getStateColor } from '@/lib/utils';
import { Brain, Sparkles, TrendingUp, Award, Clock, BookOpen, Activity } from 'lucide-react';

export default function InsightsPage() {
  const [insight, setInsight] = useState<InsightResponse | null>(null);
  const [history, setHistory] = useState<StateHistoryResponse | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [displayedAdvice, setDisplayedAdvice] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [insightData, historyData, summaryData] = await Promise.all([
          getInsightSuggestion(),
          getStateHistory(),
          getDashboardSummary(),
        ]);
        setInsight(insightData);
        setHistory(historyData);
        setSummary(summaryData);
      } catch (error) {
        console.error('Failed to fetch insights data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  useEffect(() => {
    if (insight?.instant_advice) {
      let index = 0;
      setDisplayedAdvice('');
      const timer = setInterval(() => {
        if (index < insight.instant_advice.length) {
          setDisplayedAdvice(insight.instant_advice.slice(0, index + 1));
          index++;
        } else {
          clearInterval(timer);
        }
      }, 50);
      return () => clearInterval(timer);
    }
  }, [insight]);

  const stateHistoryData = history?.records.slice(-14).map((record, index) => ({
    day: index,
    state: record.state,
    stateLabel: getStateLabel(record.state),
    stateColor: getStateColor(record.state),
    cardsReviewed: record.cards_reviewed,
    questionsAnswered: record.questions_answered,
  })) || [];

  const totalCardsReviewed = history?.records.reduce((sum, r) => sum + r.cards_reviewed, 0) || 0;
  const totalQuestionsAnswered = history?.records.reduce((sum, r) => sum + r.questions_answered, 0) || 0;
  const avgState = history?.records.length > 0
    ? history.records[history.records.length - 1].state
    : 'flow';

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <Brain className="w-12 h-12 text-primary-500 animate-pulse mb-4" />
        <p className="text-gray-500">正在分析学习数据...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">学习洞察</h1>
          <p className="text-gray-500 mt-1">AI 驱动的个性化学习建议</p>
        </div>
      </div>

      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl p-6 text-white">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-2">AI 学习建议</h3>
            <p className="text-white/90 leading-relaxed min-h-[60px]">
              {displayedAdvice || '...'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">累计复习卡片</p>
              <p className="text-xl font-bold text-gray-800">{totalCardsReviewed}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Award className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">累计答题</p>
              <p className="text-xl font-bold text-gray-800">{totalQuestionsAnswered}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Activity className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">近期状态</p>
              <p className="text-xl font-bold" style={{ color: getStateColor(avgState) }}>
                {getStateLabel(avgState)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-orange-500" />
            </div>
            <div>
              <p className="text-sm text-gray-500">整体强度</p>
              <p className="text-xl font-bold text-gray-800">
                {((summary?.overall_memory_strength || 0) * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {summary && <RadarChartComponent chapterStrengths={summary.chapter_strengths} />}
        
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary-500" />
            学习状态趋势
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stateHistoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="day" 
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  tickFormatter={(day) => `D${day + 1}`}
                />
                <YAxis 
                  type="category"
                  dataKey="stateLabel"
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  domain={['dataMin', 'dataMax']}
                />
                <Tooltip 
                  formatter={(value: string) => [value, '状态']}
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                />
                <Line
                  type="monotone"
                  dataKey="stateLabel"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ r: 6 }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {insight?.today_plan && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-primary-500" />
            今日学习计划
          </h3>
          <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
            <p className="text-amber-800">{insight.today_plan}</p>
          </div>
        </div>
      )}

      {history && history.records.length > 0 && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-800 mb-4">学习记录</h3>
          <div className="space-y-2">
            {history.records.slice(-7).reverse().map((record) => (
              <div key={`${record.date}-${record.session_id}`} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-sm text-gray-500">{record.date}</span>
                  <span 
                    className="px-2 py-0.5 rounded-full text-xs font-medium"
                    style={{ backgroundColor: `${getStateColor(record.state)}15`, color: getStateColor(record.state) }}
                  >
                    {getStateLabel(record.state)}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>复习 {record.cards_reviewed} 张</span>
                  <span>答题 {record.questions_answered} 道</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}