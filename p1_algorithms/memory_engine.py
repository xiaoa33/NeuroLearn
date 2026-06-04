import math
from datetime import datetime, timedelta

from .schemas import CardData


def review_card(
    card: CardData,
    quality: int,
    review_time: datetime | None = None,
) -> CardData:
    if quality < 0 or quality > 5:
        raise ValueError(f"quality must be 0-5, got {quality}")

    if review_time is None:
        review_time = datetime.now()

    ef = card.easiness_factor
    repetitions = card.repetitions
    interval = 1
    if card.last_reviewed_at is not None and card.next_review_at is not None:
        prev_interval = (card.next_review_at - card.last_reviewed_at).days
    else:
        prev_interval = 0

    if quality < 3:
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(prev_interval * ef)

        repetitions += 1

    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ef < 1.3:
        ef = 1.3

    hour = review_time.hour
    sleep_bonus = False
    if 21 <= hour <= 23:
        sleep_bonus = True
        next_review = review_time.replace(hour=7, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        next_review = review_time + timedelta(days=interval)

    stability = card.stability
    if sleep_bonus:
        stability = stability * 1.2

    strength = math.exp(-interval / max(stability, 0.01))

    return CardData(
        id=card.id,
        chapter=card.chapter,
        concept=card.concept,
        front=card.front,
        back=card.back,
        difficulty=card.difficulty,
        memory_strength=round(strength, 4),
        stability=round(stability, 4),
        easiness_factor=round(ef, 4),
        repetitions=repetitions,
        next_review_at=next_review,
        last_reviewed_at=review_time,
        related_concepts=card.related_concepts,
    )


def get_memory_strength(card: CardData, at_time: datetime | None = None) -> float:
    if at_time is None:
        at_time = datetime.now()
    if card.last_reviewed_at is None:
        return card.memory_strength
    t = (at_time - card.last_reviewed_at).total_seconds() / 86400
    strength = math.exp(-t / max(card.stability, 0.01))
    return round(strength, 4)


def get_forgetting_curve(card: CardData, days: int = 7) -> list[dict]:
    if card.last_reviewed_at is not None:
        elapsed_days = (datetime.now() - card.last_reviewed_at).total_seconds() / 86400
    else:
        elapsed_days = 0
    curve = []
    for d in range(0, days + 1):
        t = elapsed_days + d
        strength = math.exp(-max(t, 0) / max(card.stability, 0.01))
        curve.append({"day": d, "strength": round(strength, 4)})
    return curve
