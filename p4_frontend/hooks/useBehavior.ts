import { useEffect, useRef, useState, useCallback } from 'react';
import { useSessionStore } from '@/store/sessionStore';
import { reportState, type StateReportResponse } from '@/lib/api';

interface BehaviorStats {
  correctRate: number;
  avgTimeZscore: number | null;
  unfocusCount: number;
}

export function useBehavior() {
  const { sessionId, samValence, samArousal, setCurrentState } = useSessionStore();
  const [currentState, setCurrentStateLocal] = useState<'flow' | 'anxiety' | 'boredom' | 'confusion' | 'fatigue'>('flow');
  const [stats, setStats] = useState<BehaviorStats>({
    correctRate: 0.5,
    avgTimeZscore: null,
    unfocusCount: 0,
  });
  
  const unfocusCountRef = useRef(0);
  const lastReportTimeRef = useRef(Date.now());
  const correctAnswersRef = useRef(0);
  const totalAnswersRef = useRef(0);
  const responseTimesRef = useRef<number[]>([]);

  const reportBehavior = useCallback(async () => {
    if (!sessionId) return;

    const now = Date.now();
    const timeSinceLastReport = now - lastReportTimeRef.current;
    
    if (timeSinceLastReport < 30000) return;
    
    lastReportTimeRef.current = now;

    const avgTime = responseTimesRef.current.length > 0
      ? responseTimesRef.current.reduce((a, b) => a + b, 0) / responseTimesRef.current.length
      : 0;
    const stdTime = responseTimesRef.current.length > 1
      ? Math.sqrt(responseTimesRef.current.reduce((sum, t) => sum + Math.pow(t - avgTime, 2), 0) / (responseTimesRef.current.length - 1))
      : 1;
    
    const avgTimeZscore = stdTime > 0 ? (avgTime - 3000) / stdTime : null;

    const payload = {
      behavior: {
        correct_rate: totalAnswersRef.current > 0 ? correctAnswersRef.current / totalAnswersRef.current : 0.5,
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
    } catch (error) {
      console.error('Failed to report state:', error);
    }

    unfocusCountRef.current = 0;
    responseTimesRef.current = [];
  }, [sessionId, samValence, samArousal, setCurrentState]);

  const recordAnswer = useCallback((isCorrect: boolean, timeMs: number) => {
    if (isCorrect) correctAnswersRef.current++;
    totalAnswersRef.current++;
    responseTimesRef.current.push(timeMs);
    if (responseTimesRef.current.length > 20) {
      responseTimesRef.current.shift();
    }
    reportBehavior();
  }, [reportBehavior]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        unfocusCountRef.current++;
      }
    };

    const handleKeyDown = () => {
      reportBehavior();
    };

    const handleMouseMove = () => {
      reportBehavior();
    };

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
      correctRate: totalAnswersRef.current > 0 ? correctAnswersRef.current / totalAnswersRef.current : 0.5,
      avgTimeZscore: null,
      unfocusCount: unfocusCountRef.current,
    });
  }, [currentState]);

  return { currentState, stats, recordAnswer };
}