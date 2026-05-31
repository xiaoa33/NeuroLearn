# 题目相关路由
# GET  /api/questions/next        → 获取下一道题（调用 P1 难度调度器决定 difficulty，再从 P2 取题）
# POST /api/questions/{id}/answer → 提交答题结果，返回是否正确、解析和推荐下一题难度
