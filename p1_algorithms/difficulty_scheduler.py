from .schemas import StateEnum


# 心流理论（Csikszentmihalyi, 1990）：难度与能力匹配时进入最优学习状态
class DifficultyScheduler:
    """
    自适应难度调度器。维护最近 3 题滑动窗口，结合状态枚举动态调整难度级别。
    难度分三级：1=简单 / 2=中等（默认）/ 3=困难。
    """

    def __init__(self, current_level: int = 2):
        if current_level not in (1, 2, 3):
            raise ValueError(f"current_level must be 1/2/3, got {current_level}")
        self.current_level = current_level
        # 窗口固定为 3 题：足以反映近期趋势，又不会对单题噪声过度响应
        self.window: list[bool] = []
        self.streak_correct: int = 0
        self.streak_wrong: int = 0

    def record_result(self, correct: bool):
        self.window.append(correct)
        if len(self.window) > 3:
            self.window = self.window[-3:]
        if correct:
            self.streak_correct += 1
            self.streak_wrong = 0
        else:
            self.streak_wrong += 1
            self.streak_correct = 0

    def next_question(self, state: StateEnum) -> int:
        # 强制降级：连续答错 3 题，优先于窗口逻辑，帮助用户建立信心
        if self.streak_wrong >= 3:
            self.current_level = 1
            self.streak_wrong = 0
            return self.current_level

        # 窗口未满 3 题，数据不足以判断趋势，维持当前难度
        if len(self.window) < 3:
            return self.current_level

        recent_accuracy = sum(self.window) / 3

        if state == StateEnum.anxiety or recent_accuracy < 0.4:
            self.current_level = max(1, self.current_level - 1)
        elif state == StateEnum.boredom or recent_accuracy > 0.85:
            self.current_level = min(3, self.current_level + 1)

        return self.current_level

    def to_dict(self) -> dict:
        return {
            "current_level": self.current_level,
            "window": self.window,
            "streak_correct": self.streak_correct,
            "streak_wrong": self.streak_wrong,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DifficultyScheduler":
        sched = cls(current_level=d["current_level"])
        sched.window = d.get("window", [])
        sched.streak_correct = d.get("streak_correct", 0)
        sched.streak_wrong = d.get("streak_wrong", 0)
        return sched


def next_difficulty(
    sched: dict,
    state: StateEnum,
    recent: list[bool],
) -> tuple[int, str]:
    """P3 调用的无状态入口。接受序列化的调度器状态，批量录入结果后返回推荐难度和原因文本。"""
    instance = DifficultyScheduler.from_dict(sched)
    for r in recent:
        instance.record_result(r)

    # reason 需在 next_question 修改 current_level 前计算，否则状态已变
    reason = ""
    if instance.streak_wrong >= 3:
        reason = "连续答错3题，已降至简单难度"
    elif state == StateEnum.anxiety:
        reason = "检测到焦虑状态，降低难度"
    elif state == StateEnum.boredom:
        reason = "检测到无聊状态，提升难度"
    elif len(instance.window) >= 3:
        acc = sum(instance.window) / 3
        if acc < 0.4:
            reason = "近期正确率偏低，降低难度"
        elif acc > 0.85:
            reason = "近期正确率很高，提升难度"

    level = instance.next_question(state)

    if not reason:
        reason = "保持当前难度"

    return level, reason
