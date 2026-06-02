import { create } from 'zustand';
import type { StateEnum } from '@/lib/api';

interface SessionStore {
  sessionId: number | null;
  currentState: StateEnum;
  duration: number;
  cardsReviewed: number;
  questionsAnswered: number;
  samValence: number;
  samArousal: number;
  setSessionId: (id: number) => void;
  setCurrentState: (state: StateEnum) => void;
  incrementDuration: () => void;
  resetDuration: () => void;
  incrementCardsReviewed: () => void;
  incrementQuestionsAnswered: () => void;
  setSAMScore: (valence: number, arousal: number) => void;
  resetSession: () => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessionId: null,
  currentState: 'flow',
  duration: 0,
  cardsReviewed: 0,
  questionsAnswered: 0,
  samValence: 5,
  samArousal: 5,
  
  setSessionId: (id) => set({ sessionId: id }),
  
  setCurrentState: (state) => set({ currentState: state }),
  
  incrementDuration: () => set((state) => ({ duration: state.duration + 1 })),
  
  resetDuration: () => set({ duration: 0 }),
  
  incrementCardsReviewed: () => set((state) => ({ cardsReviewed: state.cardsReviewed + 1 })),
  
  incrementQuestionsAnswered: () => set((state) => ({ questionsAnswered: state.questionsAnswered + 1 })),
  
  setSAMScore: (valence, arousal) => set({ samValence: valence, samArousal: arousal }),
  
  resetSession: () => set({
    sessionId: null,
    currentState: 'flow',
    duration: 0,
    cardsReviewed: 0,
    questionsAnswered: 0,
    samValence: 5,
    samArousal: 5,
  }),
}));