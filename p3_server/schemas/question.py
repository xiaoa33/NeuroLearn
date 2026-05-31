# 题目相关 Pydantic 请求/响应模型
# QuestionResponse  → GET /api/questions/next 返回体（id、stem、options、type、difficulty、chapter）
# AnswerRequest     → POST /api/questions/{id}/answer 请求体（answer、time_ms、session_id）
# AnswerResult      → POST /api/questions/{id}/answer 返回体（is_correct、explanation、next_difficulty）
