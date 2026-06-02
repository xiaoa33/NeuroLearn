const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CardResponse {
  id: number;
  concept: string;
  front: string;
  back: string;
  chapter: number;
  difficulty: number;
  memory_strength: number;
  stability: number;
  repetitions: number;
  next_review_at: string;
  last_reviewed_at?: string;
  related_concepts?: string[];
}

export interface ReviewRequest {
  quality: number;
  session_id: number;
}

export interface ReviewResponse {
  next_review_at: string;
  new_memory_strength: number;
  interval_days: number;
}

export interface CurvePoint {
  day: number;
  strength: number;
}

export interface ChapterCurve {
  chapter: number;
  points: CurvePoint[];
}

export interface CurveResponse {
  curves: ChapterCurve[];
}

export interface QuestionResponse {
  id: number;
  chapter: number;
  stem: string;
  options?: string[];
  type: string;
  difficulty: number;
  related_card_id?: number;
}

export interface AnswerRequest {
  answer: string;
  time_ms: number;
  session_id: number;
}

export interface AnswerResult {
  is_correct: boolean;
  correct_answer: string;
  explanation?: string;
  next_difficulty: number;
  reason?: string;
}

export type StateEnum = 'flow' | 'anxiety' | 'boredom' | 'confusion' | 'fatigue';

export interface BehaviorSignal {
  correct_rate: number;
  avg_time_zscore?: number;
  unfocus_count: number;
}

export interface SAMScore {
  valence: number;
  arousal: number;
}

export interface CameraScore {
  attention?: number;
  blink_rate?: number;
}

export interface StateReportRequest {
  behavior: BehaviorSignal;
  sam: SAMScore;
  camera?: CameraScore;
  session_id: number;
}

export interface StateReportResponse {
  state: StateEnum;
  score: number;
  weights: Record<string, number>;
  suggestion_text: string;
}

export interface StateRecord {
  date: string;
  session_id: number;
  state: StateEnum;
  sam_valence?: number;
  sam_arousal?: number;
  cards_reviewed: number;
  questions_answered: number;
}

export interface StateHistoryResponse {
  records: StateRecord[];
}

export interface SessionStartResponse {
  session_id: number;
  started_at: string;
}

export interface SessionEndRequest {
  final_state?: string;
  sam_valence?: number;
  sam_arousal?: number;
  cards_reviewed?: number;
  questions_answered?: number;
}

export interface SessionEndResponse {
  session_id: number;
  ended_at: string;
  duration_minutes: number;
}

export interface DashboardSummary {
  due_cards_today: number;
  streak_days: number;
  overall_memory_strength: number;
  chapter_strengths: Record<number, number>;
  recent_states: Record<string, unknown>[];
  total_cards: number;
  total_questions_answered: number;
}

export interface InsightResponse {
  instant_advice: string;
  today_plan: string;
}

async function apiFetch<T>(url: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'API request failed');
  }
  
  return response.json();
}

export async function getNextCard(chapter?: number): Promise<CardResponse> {
  const params = chapter ? `?chapter=${chapter}` : '';
  return apiFetch<CardResponse>(`/api/cards/next${params}`);
}

export async function reviewCard(id: number, quality: number, sessionId: number): Promise<ReviewResponse> {
  const body: ReviewRequest = { quality, session_id: sessionId };
  return apiFetch<ReviewResponse>(`/api/cards/${id}/review`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function getCardCurves(): Promise<CurveResponse> {
  return apiFetch<CurveResponse>('/api/cards/curve');
}

export async function getNextQuestion(chapter: number, difficulty: number): Promise<QuestionResponse> {
  return apiFetch<QuestionResponse>(`/api/questions/next?chapter=${chapter}&difficulty=${difficulty}`);
}

export async function submitAnswer(id: number, answer: string, timeMs: number, sessionId: number): Promise<AnswerResult> {
  const body: AnswerRequest = { answer, time_ms: timeMs, session_id: sessionId };
  return apiFetch<AnswerResult>(`/api/questions/${id}/answer`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function reportState(payload: StateReportRequest): Promise<StateReportResponse> {
  return apiFetch<StateReportResponse>('/api/state/report', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getStateHistory(): Promise<StateHistoryResponse> {
  return apiFetch<StateHistoryResponse>('/api/state/history');
}

export async function startSession(): Promise<SessionStartResponse> {
  return apiFetch<SessionStartResponse>('/api/sessions/start', {
    method: 'POST',
  });
}

export async function endSession(id: number, samValence?: number, samArousal?: number): Promise<SessionEndResponse> {
  const body: SessionEndRequest = {
    sam_valence: samValence,
    sam_arousal: samArousal,
  };
  return apiFetch<SessionEndResponse>(`/api/sessions/${id}/end`, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function getInsightSuggestion(): Promise<InsightResponse> {
  return apiFetch<InsightResponse>('/api/insights/suggestion');
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return apiFetch<DashboardSummary>('/api/dashboard/summary');
}