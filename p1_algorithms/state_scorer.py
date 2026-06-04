from .schemas import BehaviorSignal, SAMScore, CameraScore, StateEnum


def score_state(
    behavior: BehaviorSignal,
    sam: SAMScore,
    camera: CameraScore | None = None,
    session_duration_minutes: float = 0,
) -> tuple[StateEnum, float, dict[str, float]]:
    """
    三路信号融合状态判断，SAM 自报告为主要信号，行为数据为辅助修正。

    判断层级（优先级从高到低）：
      1. SAM 独立触发 — 不依赖答题数据，任意页面可用
      2. 行为信号辅助 — 仅当有真实答题数据时（accuracy ≠ 默认值或 z-score ≠ 0）触发
      3. 长时学习疲劳 — 学习时长 + SAM 唤醒双重确认
      4. 兜底心流

    摄像头不可用时，行为和 SAM 权重按原比例重新归一化（5:3 → 5:3，合计 1.0）。
    """
    if camera is not None:
        weights = {"behavior": 0.5, "sam": 0.3, "camera": 0.2}
    else:
        weights = {"behavior": 0.625, "sam": 0.375, "camera": 0.0}

    # ── 第一层：SAM 自报告独立触发（Russell 情绪环形模型）────────────────────
    # 唤醒 (arousal)：0=困倦/精力耗尽，10=精力充沛
    # 效价 (valence)：0=心情极差，10=心情极好

    # 疲劳：唤醒极低（用户明确报告精力耗尽，无需其他条件）
    if sam.arousal <= 2:
        return StateEnum.fatigue, 1.0, weights

    # 焦虑：心情差 + 唤醒高（紧张/有压力，Russell 模型第二象限）
    if sam.valence <= 3 and sam.arousal >= 7:
        return StateEnum.anxiety, 1.0, weights

    # 无聊：心情中性偏低 + 唤醒低（游离/提不起劲，Russell 模型第三象限）
    if sam.valence <= 4 and sam.arousal <= 3:
        return StateEnum.boredom, 1.0, weights

    # ── 第二层：行为信号辅助（有真实答题数据时才生效）───────────────────────
    # 说明：accuracy 默认 0.5，avg_time_zscore 默认 0.0（无数据时不会误触发）

    has_behavior_data = behavior.avg_time_zscore != 0.0 or behavior.accuracy != 0.5

    if has_behavior_data:
        # 焦虑：频繁答错 + 耗时显著增加 + 心情偏差（D'Mello 学习焦虑特征）
        if (behavior.accuracy <= 0.4
                and behavior.avg_time_zscore > 1.0
                and sam.valence <= 5):
            return StateEnum.anxiety, 0.8, weights

        # 困惑：正确率偏低 + 答题偏慢 + 未频繁失焦（认真在想但卡住了）
        if (behavior.accuracy < 0.6
                and behavior.avg_time_zscore > 1.0
                and behavior.unfocus_count <= 3):
            return StateEnum.confusion, 0.8, weights

        # 无聊：正确率极高 + 答题极快（内容太简单，心流理论挑战-能力失衡）
        if (behavior.accuracy >= 0.9
                and behavior.avg_time_zscore < -1.0):
            return StateEnum.boredom, 0.8, weights

    # ── 第三层：长时学习疲劳（时长 + SAM 唤醒双重确认）────────────────────
    # 单独时长不触发（可能是专注），需结合低唤醒才认定疲劳
    if session_duration_minutes >= 45 and sam.arousal <= 4:
        return StateEnum.fatigue, 0.7, weights

    # ── 兜底：心流（最优学习状态）──────────────────────────────────────────
    return StateEnum.flow, 1.0, weights
