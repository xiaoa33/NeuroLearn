// 后端 API 调用统一封装（所有页面/组件只 import 此文件，不直接写 fetch）
// 读取 NEXT_PUBLIC_API_URL 环境变量作为后端 BASE URL
//
// 需实现以下函数（详见接口契约 6.4 节）：
//   getNextCard(chapter?)              → GET /api/cards/next
//   reviewCard(id, quality, sessionId) → POST /api/cards/{id}/review
//   getCardCurves()                    → GET /api/cards/curve
//   getNextQuestion(chapter, difficulty) → GET /api/questions/next
//   submitAnswer(id, answer, timeMs, sessionId) → POST /api/questions/{id}/answer
//   reportState(payload)               → POST /api/state/report
//   getStateHistory()                  → GET /api/state/history
//   startSession()                     → POST /api/sessions/start
//   endSession(id, samValence, samArousal) → POST /api/sessions/{id}/end
//   getInsightSuggestion()             → GET /api/insights/suggestion
//   getDashboardSummary()              → GET /api/dashboard/summary
