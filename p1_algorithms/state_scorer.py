from .schemas import BehaviorSignal, SAMScore, CameraScore, StateEnum


def _match_count(conditions: list[bool]) -> float:
    return sum(1 for c in conditions if c) / len(conditions)


def score_state(
    behavior: BehaviorSignal,
    sam: SAMScore,
    camera: CameraScore | None = None,
    session_duration_minutes: float = 0,
) -> tuple[StateEnum, float, dict[str, float]]:
    if camera is not None:
        weights = {"behavior": 0.5, "sam": 0.3, "camera": 0.2}
    else:
        weights = {"behavior": 0.625, "sam": 0.375, "camera": 0.0}

    # 1. Fatigue — 连续学习 ≥45min + 唤醒极低 + 正确率偏低
    conditions = [
        session_duration_minutes >= 45,
        sam.arousal <= 3,
        behavior.accuracy < 0.6,
    ]
    if all(conditions):
        return StateEnum.fatigue, _match_count(conditions), weights

    # 2. Anxiety — 正确率 ≤40% + 耗时显著上升 + 低效价高唤醒
    conditions = [
        behavior.accuracy <= 0.4,
        behavior.avg_time_zscore > 1.0,
        sam.valence <= 4 and sam.arousal >= 7,
    ]
    if all(conditions):
        return StateEnum.anxiety, _match_count(conditions), weights

    # 3. Confusion — 错误率高 + 耗时高 + 失焦不多
    conditions = [
        behavior.accuracy < 0.6,
        behavior.avg_time_zscore > 1.0,
        behavior.unfocus_count <= 3,
    ]
    if all(conditions):
        return StateEnum.confusion, _match_count(conditions), weights

    # 4. Boredom — 正确率 ≥95% + 耗时远低于均值 + 中性效价低唤醒
    conditions = [
        behavior.accuracy >= 0.95,
        behavior.avg_time_zscore < -1.0,
        4 <= sam.valence <= 6 and sam.arousal <= 3,
    ]
    if all(conditions):
        return StateEnum.boredom, _match_count(conditions), weights

    # 5. Flow — 兜底
    return StateEnum.flow, 1.0, weights
