'use client';

import { useState, useEffect, useRef } from 'react';
import type { QuestionResponse, AnswerResult } from '@/lib/api';
import { getDifficultyLabel, getDifficultyColor } from '@/lib/utils';
import { Check, X, Lightbulb } from 'lucide-react';

interface QuestionCardProps {
  question: QuestionResponse;
  onAnswer: (answer: string, timeMs: number) => Promise<AnswerResult>;
  onResult: (result: AnswerResult) => void;
}

export function QuestionCard({ question, onAnswer, onResult }: QuestionCardProps) {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [result, setResult] = useState<AnswerResult | null>(null);
  const [showScore, setShowScore] = useState(false);
  const startTimeRef = useRef(Date.now());

  useEffect(() => {
    setSelectedAnswer(null);
    setShowResult(false);
    setResult(null);
    setShowScore(false);
    startTimeRef.current = Date.now();
  }, [question.id]);

  const handleSelectAnswer = async (answer: string) => {
    if (showResult) return;
    
    setSelectedAnswer(answer);
    const timeMs = Date.now() - startTimeRef.current;
    
    const answerResult = await onAnswer(answer, timeMs);
    setResult(answerResult);
    setShowResult(true);
    onResult(answerResult);
    
    if (answerResult.is_correct) {
      setShowScore(true);
      setTimeout(() => setShowScore(false), 1500);
    }
  };

  const difficultyColor = getDifficultyColor(question.difficulty);
  const options = question.options || ['A', 'B', 'C', 'D'];

  const getOptionLabel = (index: number) => {
    return String.fromCharCode(65 + index);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl mx-auto">
      {showScore && result?.is_correct && (
        <div className="absolute top-4 right-4 animate-float-up text-green-500 font-bold text-2xl">
          +10
        </div>
      )}
      
      <div className="flex items-center justify-between mb-6">
        <span 
          className="px-3 py-1 rounded-full text-xs font-medium"
          style={{ backgroundColor: `${difficultyColor}15`, color: difficultyColor }}
        >
          {getDifficultyLabel(question.difficulty)}
        </span>
        <span className="text-sm text-gray-500">
          第 {question.id} 题
        </span>
      </div>
      
      <h2 className="text-xl font-semibold text-gray-800 mb-8 text-center">
        {question.stem}
      </h2>
      
      <div className="space-y-3">
        {options.map((option, index) => {
          const label = getOptionLabel(index);
          const isSelected = selectedAnswer === label;
          const isCorrect = showResult && result?.correct_answer === label;
          const isWrong = showResult && isSelected && !isCorrect;
          
          let buttonClass = 'bg-gray-50 hover:bg-gray-100 border-gray-200 text-gray-700';
          if (isCorrect) buttonClass = 'bg-green-50 border-green-500 text-green-700';
          if (isWrong) buttonClass = 'bg-red-50 border-red-500 text-red-700';
          if (isSelected && !showResult) buttonClass = 'bg-primary-50 border-primary-500 text-primary-700';
          
          return (
            <button
              key={label}
              onClick={() => handleSelectAnswer(label)}
              disabled={showResult}
              className={`w-full p-4 rounded-xl border-2 text-left transition-all duration-200 flex items-center gap-4 ${buttonClass}`}
            >
              <span className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold ${
                isCorrect ? 'bg-green-500 text-white' :
                isWrong ? 'bg-red-500 text-white' :
                isSelected ? 'bg-primary-500 text-white' :
                'bg-white text-gray-600'
              }`}>
                {isCorrect && showResult ? <Check className="w-4 h-4" /> :
                 isWrong && showResult ? <X className="w-4 h-4" /> :
                 label}
              </span>
              <span className="flex-1">{option}</span>
            </button>
          );
        })}
      </div>
      
      {showResult && result?.explanation && (
        <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-xl animate-fade-in">
          <div className="flex items-start gap-3">
            <Lightbulb className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-amber-800 mb-1">解析</p>
              <p className="text-sm text-amber-700">{result.explanation}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}