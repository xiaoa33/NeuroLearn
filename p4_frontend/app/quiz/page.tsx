'use client';

import { useState, useEffect, useCallback } from 'react';
import { getNextQuestion, submitAnswer, type QuestionResponse, type AnswerResult } from '@/lib/api';
import { useSessionStore } from '@/store/sessionStore';
import { recordAnswer } from '@/hooks/useBehavior';
import { QuestionCard } from '@/components/quiz/QuestionCard';
import { DifficultyBadge } from '@/components/quiz/DifficultyBadge';
import { SAMSlider } from '@/components/state/SAMSlider';
import { HelpCircle, Loader2 } from 'lucide-react';

const CHAPTERS = [
  { id: 1, name: '绪论' },
  { id: 2, name: '方法与技术' },
  { id: 3, name: '细胞机制与认知' },
  { id: 4, name: '神经解剖和发展' },
  { id: 7, name: '物体识别' },
  { id: 8, name: '学习与记忆' },
  { id: 9, name: '运动控制' },
  { id: 10, name: '情绪' },
  { id: 11, name: '语言' },
  { id: 12, name: '注意与意识' },
];

export default function QuizPage() {
  const [question, setQuestion] = useState<QuestionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentChapter, setCurrentChapter] = useState(1);
  const [currentDifficulty, setCurrentDifficulty] = useState(2);
  const [previousDifficulty, setPreviousDifficulty] = useState<number | undefined>(undefined);
  const [score, setScore] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const { sessionId, currentState, incrementQuestionsAnswered } = useSessionStore();

  const fetchNextQuestion = useCallback(async (chapter: number, difficulty: number) => {
    setLoading(true);
    try {
      const nextQuestion = await getNextQuestion(chapter, difficulty);
      setQuestion(nextQuestion);
    } catch (error) {
      console.error('Failed to fetch next question:', error);
      setQuestion(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNextQuestion(currentChapter, currentDifficulty);
  }, [currentChapter]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleAnswer = async (answer: string, timeMs: number): Promise<AnswerResult> => {
    if (!question || !sessionId) {
      return { is_correct: false, correct_answer: '', next_difficulty: currentDifficulty };
    }
    const result = await submitAnswer(question.id, answer, timeMs, sessionId, currentState);
    recordAnswer(result.is_correct, timeMs);
    incrementQuestionsAnswered();
    return result;
  };

  const handleResult = (result: AnswerResult) => {
    setTotalCount(prev => prev + 1);
    if (result.is_correct) {
      setCorrectCount(prev => prev + 1);
      setScore(prev => prev + 10);
    }
  };

  const handleNext = (nextDifficulty: number) => {
    if (nextDifficulty !== currentDifficulty) {
      setPreviousDifficulty(currentDifficulty);
      setCurrentDifficulty(nextDifficulty);
    }
    fetchNextQuestion(currentChapter, nextDifficulty);
  };

  const handleChapterChange = (chapterId: number) => {
    setCurrentChapter(chapterId);
    setCurrentDifficulty(2);
    setPreviousDifficulty(undefined);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
        <p className="text-gray-500">正在加载题目...</p>
      </div>
    );
  }

  if (!question) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh]">
        <HelpCircle className="w-16 h-16 text-gray-300 mb-4" />
        <p className="text-gray-500">暂无题目</p>
        <p className="text-gray-400 text-sm mt-1">请确保已生成题目</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">章节测验</h1>
          <p className="text-gray-500 mt-1">检验你的知识掌握程度</p>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-center">
            <p className="text-sm text-gray-500">得分</p>
            <p className="text-2xl font-bold text-primary-600">{score}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500">正确率</p>
            <p className="text-2xl font-bold text-green-600">
              {totalCount > 0 ? ((correctCount / totalCount) * 100).toFixed(0) : 0}%
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3 mb-6">
        <div className="flex gap-2 overflow-x-auto pb-2 flex-1 min-w-0" style={{ scrollbarWidth: 'thin' }}>
          {CHAPTERS.map(chapter => (
            <button
              key={chapter.id}
              onClick={() => handleChapterChange(chapter.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                currentChapter === chapter.id
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {chapter.name}
            </button>
          ))}
        </div>
        <div className="flex-shrink-0">
          <DifficultyBadge difficulty={currentDifficulty} previousDifficulty={previousDifficulty} />
        </div>
      </div>

      <QuestionCard
        question={question}
        onAnswer={handleAnswer}
        onResult={handleResult}
        onNext={handleNext}
      />

      <div className="mt-6 max-w-2xl mx-auto">
        <h3 className="text-sm font-medium text-gray-600 mb-3 text-center">自我评估状态</h3>
        <SAMSlider />
      </div>
    </div>
  );
}
