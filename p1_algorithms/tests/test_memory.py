from datetime import datetime, timedelta
import pytest

from ..schemas import CardData
from ..memory_engine import review_card, get_memory_strength, get_forgetting_curve


def make_card(**overrides) -> CardData:
    defaults = {
        "id": 1,
        "chapter": 8,
        "concept": "LTP",
        "front": "LTP 的突触机制是什么？",
        "back": "突触传递效能持久增强。",
        "difficulty": 2,
        "memory_strength": 1.0,
        "stability": 2.0,
        "easiness_factor": 2.5,
        "repetitions": 0,
        "next_review_at": datetime(2026, 6, 2, 10, 0),
        "last_reviewed_at": datetime(2026, 6, 1, 10, 0),
    }
    defaults.update(overrides)
    return CardData(**defaults)


class TestReviewCardQuality:
    def test_quality_0_resets(self):
        card = make_card(repetitions=3, easiness_factor=2.3, stability=3.0)
        t = datetime(2026, 6, 2, 10, 0)
        result = review_card(card, quality=0, review_time=t)
        assert result.repetitions == 0
        assert result.next_review_at == t + timedelta(days=1)

    def test_quality_3_first_review(self):
        card = make_card(repetitions=0, easiness_factor=2.5, stability=1.0)
        t = datetime(2026, 6, 2, 10, 0)
        result = review_card(card, quality=3, review_time=t)
        assert result.repetitions == 1
        assert result.next_review_at == t + timedelta(days=1)

    def test_quality_4_second_review(self):
        card = make_card(repetitions=1, easiness_factor=2.5)
        t = datetime(2026, 6, 2, 10, 0)
        result = review_card(card, quality=4, review_time=t)
        assert result.repetitions == 2
        assert result.next_review_at == t + timedelta(days=6)

    def test_quality_5_third_review(self):
        card = make_card(
            repetitions=2, easiness_factor=2.5,
            last_reviewed_at=datetime(2026, 5, 28, 10, 0),
            next_review_at=datetime(2026, 6, 2, 10, 0),
        )
        t = datetime(2026, 6, 2, 10, 0)
        result = review_card(card, quality=5, review_time=t)
        assert result.repetitions == 3
        expected_interval = round(5 * 2.5)
        assert result.next_review_at == t + timedelta(days=expected_interval)

    def test_quality_out_of_range(self):
        card = make_card()
        with pytest.raises(ValueError):
            review_card(card, quality=-1)
        with pytest.raises(ValueError):
            review_card(card, quality=6)


class TestEasinessFactor:
    def test_ef_never_below_1_3(self):
        card = make_card(easiness_factor=1.3)
        result = review_card(card, quality=0, review_time=datetime(2026, 6, 2, 10, 0))
        assert result.easiness_factor >= 1.3

    def test_ef_increases_on_high_quality(self):
        card = make_card(easiness_factor=2.5)
        result = review_card(card, quality=5, review_time=datetime(2026, 6, 2, 10, 0))
        assert result.easiness_factor > 2.5

    def test_ef_decreases_on_low_quality(self):
        card = make_card(easiness_factor=2.5)
        result = review_card(card, quality=1, review_time=datetime(2026, 6, 2, 10, 0))
        assert result.easiness_factor < 2.5


class TestSleepFactor:
    def test_night_review_bumps_to_morning(self):
        card = make_card(repetitions=1, easiness_factor=2.5)
        t = datetime(2026, 6, 2, 22, 0)  # 22:00
        result = review_card(card, quality=4, review_time=t)
        assert result.next_review_at.hour == 7
        assert result.next_review_at.day == 3  # next day

    def test_morning_review_normal_schedule(self):
        card = make_card(repetitions=1, easiness_factor=2.5)
        t = datetime(2026, 6, 2, 10, 0)
        result = review_card(card, quality=4, review_time=t)
        assert result.next_review_at.hour == 10

    def test_sleep_bonus_increases_stability(self):
        card = make_card(stability=2.0)
        t = datetime(2026, 6, 2, 22, 0)
        result = review_card(card, quality=4, review_time=t)
        assert result.stability == round(2.0 * 1.2, 4)


class TestMemoryStrength:
    def test_strength_at_review_time_is_high(self):
        card = make_card(
            stability=2.0,
            last_reviewed_at=datetime(2026, 6, 2, 10, 0),
        )
        strength = get_memory_strength(card, at_time=datetime(2026, 6, 2, 10, 0))
        assert strength == 1.0

    def test_strength_decays_over_time(self):
        card = make_card(
            stability=2.0,
            last_reviewed_at=datetime(2026, 6, 1, 10, 0),
        )
        strength = get_memory_strength(card, at_time=datetime(2026, 6, 3, 10, 0))
        assert strength < 0.5

    def test_no_review_returns_stored_strength(self):
        card = make_card(last_reviewed_at=None, memory_strength=0.8)
        strength = get_memory_strength(card)
        assert strength == 0.8


class TestForgettingCurve:
    def test_curve_length(self):
        card = make_card(
            stability=2.0,
            last_reviewed_at=datetime(2026, 6, 1, 10, 0),
        )
        curve = get_forgetting_curve(card, days=7)
        assert len(curve) == 8  # day 0 through day 7

    def test_curve_monotonically_decreasing(self):
        card = make_card(
            stability=2.0,
            last_reviewed_at=datetime(2026, 6, 1, 10, 0),
        )
        curve = get_forgetting_curve(card, days=7)
        strengths = [p["strength"] for p in curve]
        for i in range(1, len(strengths)):
            assert strengths[i] <= strengths[i - 1]
