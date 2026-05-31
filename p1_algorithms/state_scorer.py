# 学习状态评分算法（三路信号加权融合）
# 实现纯函数：
#   score_state(behavior, sam, camera=None)
#       → 输出状态枚举(flow/anxiety/boredom/confusion/fatigue) + 得分 + 实际权重
# 融合规则：行为信号×0.5 + SAM自报告×0.3 + 摄像头×0.2
# 摄像头不可用时自动重新归一化：行为×0.625 + SAM×0.375
# 理论依据：Russell 情绪环形模型 + D'Mello & Graesser 学习情绪体系（课程第9、11章）
