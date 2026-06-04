import { useEffect, useRef } from 'react';
import { useSessionStore } from '@/store/sessionStore';
import { startSession } from '@/lib/api';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useSession() {
  const { sessionId, setSessionId } = useSessionStore();
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    if (useSessionStore.getState().sessionId) return;

    startSession()
      .then((res) => setSessionId(res.session_id))
      .catch((err) => console.error('Failed to start session:', err));
  }, []);

  useEffect(() => {
    const handleBeforeUnload = () => {
      const { sessionId, samValence, samArousal, cardsReviewed, questionsAnswered, currentState } =
        useSessionStore.getState();
      if (!sessionId) return;

      // keepalive: true 确保浏览器关闭/跳转时请求仍能完成
      fetch(`${BASE_URL}/api/sessions/${sessionId}/end`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        keepalive: true,
        body: JSON.stringify({
          final_state: currentState,
          sam_valence: samValence,
          sam_arousal: samArousal,
          cards_reviewed: cardsReviewed,
          questions_answered: questionsAnswered,
        }),
      }).catch(console.error);
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, []);

  return { sessionId };
}
