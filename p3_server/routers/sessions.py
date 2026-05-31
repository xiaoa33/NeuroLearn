# 学习会话相关路由（P4 最先调用，优先实现）
# POST /api/sessions/start      → 创建新学习会话，返回 session_id（前端全局持有）
# POST /api/sessions/{id}/end   → 结束会话，写入 ended_at 和 SAM 最终得分
