# 学习状态相关路由
# POST /api/state/report   → 接收三路信号（行为指标 + SAM 量表），调用 P1 评分算法，返回状态枚举和建议
# GET  /api/state/history  → 返回最近7天状态变化时序记录，供 Insights 页面绘制趋势图
