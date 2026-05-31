# 间隔重复引擎（SM-2 算法 + 睡眠因子修正）
# 实现三个纯函数：
#   review_card(card, quality)         → 根据用户评分(0-5)计算下次复习时间和新记忆强度
#   get_memory_strength(card)          → 返回当前记忆保留率 float(0~1)，基于遗忘曲线公式 R=e^(-t/S)
#   get_forgetting_curve(card, days)   → 预测未来 N 天的记忆强度列表，供前端折线图使用
# 无数据库依赖，无网络调用，纯计算逻辑
