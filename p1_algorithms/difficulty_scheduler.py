# 自适应难度调度器
# 实现纯函数：
#   next_difficulty(sched, state, recent_results) → 推荐难度 int(1/2/3) + 调整原因字符串
# 维护最近3题滑动窗口，结合状态枚举动态升降难度：
#   焦虑/正确率<40% → 降级；无聊/正确率>85% → 升级
#   连续答错3题 → 强制降到 Easy；连续答对5题 Hard → 奖励提示
# P3 在 quiz_service 中调用此函数决定下一题难度
