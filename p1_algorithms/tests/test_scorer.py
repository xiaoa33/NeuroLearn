from ..schemas import BehaviorSignal, SAMScore, CameraScore, StateEnum
from ..state_scorer import score_state


class TestWeightNormalization:
    def test_with_camera(self):
        behavior = BehaviorSignal(accuracy=0.9, avg_time_zscore=0.0, unfocus_count=1, pause_duration=5.0)
        sam = SAMScore(valence=7, arousal=5)
        camera = CameraScore(focus_score=0.8, blink_rate=15, head_offset=0.1)
        _, _, weights = score_state(behavior, sam, camera)
        assert weights == {"behavior": 0.5, "sam": 0.3, "camera": 0.2}

    def test_without_camera(self):
        behavior = BehaviorSignal(accuracy=0.9, avg_time_zscore=0.0, unfocus_count=1, pause_duration=5.0)
        sam = SAMScore(valence=7, arousal=5)
        _, _, weights = score_state(behavior, sam, camera=None)
        assert weights["behavior"] == 0.625
        assert weights["sam"] == 0.375
        assert weights["camera"] == 0.0


class TestFlowDetection:
    def test_strong_flow_signal(self):
        behavior = BehaviorSignal(accuracy=0.85, avg_time_zscore=0.1, unfocus_count=1, pause_duration=3.0)
        sam = SAMScore(valence=7, arousal=5)
        state, score, _ = score_state(behavior, sam)
        assert state == StateEnum.flow
        assert score > 0.5


class TestAnxietyDetection:
    def test_strong_anxiety_signal(self):
        behavior = BehaviorSignal(accuracy=0.3, avg_time_zscore=1.5, unfocus_count=2, pause_duration=10.0)
        sam = SAMScore(valence=3, arousal=8)
        state, score, _ = score_state(behavior, sam)
        assert state == StateEnum.anxiety
        assert score > 0.5


class TestBoredomDetection:
    def test_strong_boredom_signal(self):
        behavior = BehaviorSignal(accuracy=0.98, avg_time_zscore=-1.5, unfocus_count=5, pause_duration=2.0)
        sam = SAMScore(valence=5, arousal=2)
        state, score, _ = score_state(behavior, sam)
        assert state == StateEnum.boredom
        assert score > 0.5


class TestConfusionDetection:
    def test_strong_confusion_signal(self):
        behavior = BehaviorSignal(accuracy=0.4, avg_time_zscore=1.5, unfocus_count=2, pause_duration=8.0)
        sam = SAMScore(valence=5, arousal=6)
        state, score, _ = score_state(behavior, sam)
        assert state == StateEnum.confusion
        assert score > 0.5


class TestFatigueDetection:
    def test_fatigue_after_long_session(self):
        behavior = BehaviorSignal(accuracy=0.5, avg_time_zscore=0.5, unfocus_count=3, pause_duration=15.0)
        sam = SAMScore(valence=4, arousal=2)
        state, score, _ = score_state(behavior, sam, session_duration_minutes=50)
        assert state == StateEnum.fatigue
        assert score > 0.5

    def test_not_fatigued_in_short_session(self):
        behavior = BehaviorSignal(accuracy=0.5, avg_time_zscore=0.5, unfocus_count=3, pause_duration=15.0)
        sam = SAMScore(valence=4, arousal=2)
        state, _, _ = score_state(behavior, sam, session_duration_minutes=10)
        assert state != StateEnum.fatigue
