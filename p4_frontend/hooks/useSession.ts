import { useEffect } from 'react';
import { useSessionStore } from '@/store/sessionStore';
import { startSession, endSession } from '@/lib/api';

export function useSession() {
  const { sessionId, setSessionId, samValence, samArousal } = useSessionStore();

  useEffect(() => {
    let isMounted = true;
    
    const initializeSession = async () => {
      try {
        const response = await startSession();
        if (isMounted) {
          setSessionId(response.session_id);
        }
      } catch (error) {
        console.error('Failed to start session:', error);
      }
    };

    initializeSession();

    const handleBeforeUnload = async () => {
      if (sessionId) {
        try {
          await endSession(sessionId, samValence, samArousal);
        } catch (error) {
          console.error('Failed to end session:', error);
        }
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      isMounted = false;
      window.removeEventListener('beforeunload', handleBeforeUnload);
      if (sessionId) {
        endSession(sessionId, samValence, samArousal).catch(console.error);
      }
    };
  }, [sessionId, setSessionId, samValence, samArousal]);

  return { sessionId };
}