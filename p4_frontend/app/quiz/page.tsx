'use client';

import { useState, useEffect } from 'react';
import { getNextQuestion, submitAnswer, type QuestionResponse, type AnswerResult } from '@/lib/api';
import { useSessionStore } from '@/store/sessionStore';
import { QuestionCard } from '@/components/quiz/QuestionCard';
import { DifficultyBadge } from '@/components/quiz/DifficultyBadge';
import { getChapterName } from '@/lib/utils';
import { HelpCircle, Loader2, Trophy } from 'lucide-react';

const chapters = [
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
  const { sessionId, incrementQuestionsAnswered } = useSessionStore();

  useEffect(() => {
    fetchNextQuestion();
  }, [currentChapter, currentDifficulty]);

  const fetchNextQuestion = async () => {
    setLoading(true);
    try {
      const nextQuestion = await getNextQuestion(currentChapter, currentDifficulty);
      setQuestion(nextQuestion);
    } catch (error) {
      console.error('Failed to fetch next question:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer: string, timeMs: number): Promise<AnswerResult> => {
    if (!question || !sessionId) {
      return { is_correct: false, correct_answer: '', next_difficulty: currentDifficulty };
    }

    const result = await submitAnswer(question.id, answer, timeMs, sessionId);
    incrementQuestionsAnswered();
    return result;
  };

  const handleResult = (result: AnswerResult) => {
    setTotalCount(prev => prev + 1);
    if (result.is_correct) {
      setCorrectCount(prev => prev + 1);
      setScore(prev => prev + 10);
    }
    
    if (result.next_difficulty !== currentDifficulty) {
      setPreviousDifficulty(currentDifficulty);
      setCurrentDifficulty(result.next_difficulty);
    }
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

      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
          {chapters.map(chapter => (
            <button
              key={chapter.id}
              onClick={() => {
                setCurrentChapter(chapter.id);
                setCurrentDifficulty(2);
              }}
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
        <DifficultyBadge difficulty={currentDifficulty} previousDifficulty={previousDifficulty} />
      </div>

      <QuestionCard
        question={question}
        onAnswer={handleAnswer}
        onResult={handleResult}
      />

      <div className="mt-6 flex justify-center gap-4">
        <button
          onClick={() => {
            if (currentDifficulty > 1) {
              setPreviousDifficulty(currentDifficulty);
              setCurrentDifficulty(currentDifficulty - 1);
            }
          }}
          disabled={currentDifficulty <= 1}
          className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          降低难度
        </button>
        <button
          onClick={() => {
            if (currentDifficulty < 3) {
              setPreviousDifficulty(currentDifficulty);
              setCurrentDifficulty(currentDifficulty + 1);
            }
          }}
          disabled={currentDifficulty >= 3}
          className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          提升难度
        </button>
      </div>
    </div>
  );
}