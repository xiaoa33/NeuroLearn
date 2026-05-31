# 学习状态业务逻辑编排
# 接收三路信号 → 调用 P1 state_scorer 计算状态枚举 → 调用 P2 db_service 存入会话日志
# 返回状态枚举和即时建议文本，供 routers/state.py 使用
