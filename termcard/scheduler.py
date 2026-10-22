from datetime import date, timedelta

AGAIN, HARD, GOOD, EASY = 0, 3, 4, 5


def review_card(card, quality):
    """SM-2 spaced repetition algorithm."""
    if quality < 3:
        card.repetitions = 0
        card.interval = 1
    else:
        if card.repetitions == 0:
            card.interval = 1
        elif card.repetitions == 1:
            card.interval = 6
        else:
            card.interval = max(1, round(card.interval * card.ease_factor))
        card.repetitions += 1

    card.ease_factor = max(
        1.3,
        card.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)),
    )
    card.due = (date.today() + timedelta(days=card.interval)).isoformat()
    card.last_reviewed = date.today().isoformat()
    card.total_reviews += 1
    return card
