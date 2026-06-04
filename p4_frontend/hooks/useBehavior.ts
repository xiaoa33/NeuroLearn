import { useEffect, useRef, useState, useCallback } from 'react';
import { useSessionStore } from '@/store/sessionStore';
import { reportState, type StateReportResponse } from '@/lib/api';

interface BehaviorStats {
  correctRate: number;
  avgTimeZscore: number | null;
  unfocusCount: number;
}

// 模块级共享变量：任何页面调用 recordAnswer() 都写入同一份数据
// useBehavior 的 reportBehavior 每 30s 读取并上报后重置 times
let _correctAnswers = 0;
let _totalAnswers = 0;
let _responseTimes: number[] = [];

/**
 * 记录一次答题结果。quiz 页面在提交答案后调用。
 * 数据由 BehaviorTracker（useBehavior）统一汇总上报，无需额外网络请求。
 */
export function recordAnswer(isCorrect: boolean, timeMs: number) {
  if (isCorrect) _correctAnswers++;
  _totalAnswers++;
  _responseTimes.push(timeMs);
  if (_responseTimes.length > 20) _responseTimes.shift();
}

export function useBehavior() {
  const { sessionId, samValence, samArousal, setCurrentState, setStateSuggestion } = useSessionStore();
  const [currentState, setCurrentStateLocal] = useState<'flow' | 'anxiety' | 'boredom' | 'confusion' | 'fatigue'>('flow');
  const [stats, setStats] = useState<BehaviorStats>({
    correctRate: 0.5,
    avgTimeZscore: null,
    unfocusCount: 0,
  });

  const unfocusCountRef = useRef(0);
  const lastReportTimeRef = useRef(Date.now());

  const reportBehavior = useCallback(async () => {
    if (!sessionId) return;

    const now = Date.now();
    if (now - lastReportTimeRef.current < 30000) return;
    lastReportTimeRef.current = now;

    // 读取模块级答题数据
    const correctRate = _totalAnswers > 0 ? _correctAnswers / _totalAnswers : 0.5;
    const times = _responseTimes;
    const avgTime = times.length > 0
      ? times.reduce((a, b) => a + b, 0) / times.length
      : 0;
    const stdTime = times.length > 1
      ? Math.sqrt(times.reduce((sum, t) => sum + Math.pow(t - avgTime, 2), 0) / (times.length - 1))
      : 1;
    const avgTimeZscore = times.length > 0 ? (avgTime - 3000) / stdTime : null;

    const payload = {
      behavior: {
        correct_rate: correctRate,
        avg_time_zscore: avgTimeZscore,
        unfocus_count: unfocusCountRef.current,
      },
      sam: {
        valence: samValence,
        arousal: samArousal,
      },
      session_id: sessionId,
    };

    try {
      const response: StateReportResponse = await reportState(payload);
      setCurrentState(response.state);
      setCurrentStateLocal(response.state);
      if (response.suggestion_text) setStateSuggestion(response.suggestion_text);
    } catch (error) {
      console.error('Failed to report state:', error);
    }

    // 每次上报后重置窗口数据（correct/total 保留作为滚动正确率，times 重置用于下轮 zscore）
    unfocusCountRef.current = 0;
    _responseTimes = [];
  }, [sessionId, samValence, samArousal, setCurrentState, setStateSuggestion]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        unfocusCountRef.current++;
      }
    };

    const handleKeyDown = () => { reportBehavior(); };
    const handleMouseMove = () => { reportBehavior(); };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousemove', handleMouseMove);

    const interval = setInterval(reportBehavior, 30000);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousemove', handleMouseMove);
      clearInterval(interval);
    };
  }, [reportBehavior]);

  useEffect(() => {
    setStats({
      correctRate: _totalAnswers > 0 ? _correctAnswers / _totalAnswers : 0.5,
      avgTimeZscore: null,
      unfocusCount: unfocusCountRef.current,
    });
  }, [currentState]);

  return { currentState, stats };
}
