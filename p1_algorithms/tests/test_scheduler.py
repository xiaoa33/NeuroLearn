import pytest

from ..schemas import StateEnum
from ..difficulty_scheduler import DifficultyScheduler, next_difficulty


class TestDifficultyScheduler:
    def test_default_level_is_medium(self):
        sched = DifficultyScheduler()
        assert sched.current_level == 2

    def test_custom_start_level(self):
        sched = DifficultyScheduler(current_level=1)
        assert sched.current_level == 1

    def test_invalid_level_raises(self):
        with pytest.raises(ValueError):
            DifficultyScheduler(current_level=0)
        with pytest.raises(ValueError):
            DifficultyScheduler(current_level=4)

    def test_maintains_level_without_enough_data(self):
        sched = DifficultyScheduler()
        sched.record_result(True)
        level = sched.next_question(StateEnum.flow)
        assert level == 2

    def test_window_limits_to_3(self):
        sched = DifficultyScheduler()
        for _ in range(5):
            sched.record_result(True)
        assert len(sched.window) == 3

    def test_lower_level_on_anxiety(self):
        sched = DifficultyScheduler()
        for _ in range(3):
            sched.record_result(False)
        level = sched.next_question(StateEnum.anxiety)
        assert level == 1

    def test_raise_level_on_boredom(self):
        sched = DifficultyScheduler()
        for _ in range(3):
            sched.record_result(True)
        level = sched.next_question(StateEnum.boredom)
        assert level == 3

    def test_lower_level_on_low_accuracy(self):
        sched = DifficultyScheduler()
        sched.record_result(True)
        sched.record_result(False)
        sched.record_result(False)
        level = sched.next_question(StateEnum.flow)
        assert level == 1

    def test_raise_level_on_high_accuracy(self):
        sched = DifficultyScheduler()
        for _ in range(3):
            sched.record_result(True)
        level = sched.next_question(StateEnum.flow)
        assert level == 3

    def test_cannot_go_below_1(self):
        sched = DifficultyScheduler(current_level=1)
        for _ in range(3):
            sched.record_result(False)
        level = sched.next_question(StateEnum.anxiety)
        assert level == 1

    def test_cannot_go_above_3(self):
        sched = DifficultyScheduler(current_level=3)
        for _ in range(3):
            sched.record_result(True)
        level = sched.next_question(StateEnum.boredom)
        assert level == 3

    def test_streak_3_wrong_forces_easy(self):
        sched = DifficultyScheduler(current_level=3)
        for _ in range(3):
            sched.record_result(False)
        level = sched.next_question(StateEnum.flow)
        assert level == 1

    def test_streak_correct_tracks(self):
        sched = DifficultyScheduler()
        sched.record_result(True)
        sched.record_result(True)
        assert sched.streak_correct == 2
        sched.record_result(False)
        assert sched.streak_correct == 0
        assert sched.streak_wrong == 1

    def test_serialization_roundtrip(self):
        sched = DifficultyScheduler(current_level=2)
        sched.record_result(True)
        sched.record_result(False)
        d = sched.to_dict()
        restored = DifficultyScheduler.from_dict(d)
        assert restored.current_level == sched.current_level
        assert restored.window == sched.window
        assert restored.streak_correct == sched.streak_correct
        assert restored.streak_wrong == sched.streak_wrong


class TestNextDifficultyFunction:
    def test_returns_level_and_reason(self):
        sched_dict = {"current_level": 2, "window": [], "streak_correct": 0, "streak_wrong": 0}
        level, reason = next_difficulty(sched_dict, StateEnum.flow, [True, True, False])
        assert level in (1, 2, 3)
        assert isinstance(reason, str)
        assert len(reason) > 0

    def test_anxiety_triggers_downgrade_reason(self):
        sched_dict = {"current_level": 2, "window": [True, True, True], "streak_correct": 3, "streak_wrong": 0}
        level, reason = next_difficulty(sched_dict, StateEnum.anxiety, [False, True, True])
        assert level == 1
        assert "焦虑" in reason

    def test_boredom_triggers_upgrade_reason(self):
        sched_dict = {"current_level": 2, "window": [True, True, True], "streak_correct": 3, "streak_wrong": 0}
        level, reason = next_difficulty(sched_dict, StateEnum.boredom, [True, True, True])
        assert level == 3
        assert "无聊" in reason
