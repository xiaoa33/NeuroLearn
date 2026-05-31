# 卡片相关 Pydantic 请求/响应模型
# CardResponse      → GET /api/cards/next 返回体（id、concept、front、back、memory_strength、chapter）
# ReviewRequest     → POST /api/cards/{id}/review 请求体（quality、session_id）
# ReviewResponse    → POST /api/cards/{id}/review 返回体（next_review_at、new_memory_strength、interval_days）
# CurveResponse     → GET /api/cards/curve 返回体
