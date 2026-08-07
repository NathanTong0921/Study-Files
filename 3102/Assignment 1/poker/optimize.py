from __future__ import annotations

from itertools import combinations

from hand_rank import HandRank

RANK_VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}

INDEX_COMBOS = tuple(combinations(range(7), 5))

def _value(card: str) -> int:
    return RANK_VALUES[card[0]]

def _counts(values: list[int]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts

def _straight_order(distinct: list[int]) -> list[int] | None:
    if len(distinct) != 5:
        return None
    if distinct == [2, 3, 4, 5, 14]:
        return [5, 4, 3, 2, 14]
    if distinct[4] - distinct[0] == 4:
        return sorted(distinct, reverse=True)
    return None

def _score_five(cards: list[str]) -> tuple[HandRank, list[str], tuple[int, tuple[int, ...]]]:
    values = [_value(card) for card in cards]
    counts = _counts(values)
    distinct = sorted(counts)
    straight = _straight_order(distinct)
    is_flush = len({card[1] for card in cards}) == 1
    pattern = sorted(counts.values(), reverse=True)

    if straight is not None and is_flush and straight == [14, 13, 12, 11, 10]:
        rank = HandRank.ROYAL_FLUSH
    elif straight is not None and is_flush:
        rank = HandRank.STRAIGHT_FLUSH
    elif pattern == [4, 1]:
        rank = HandRank.FOUR_OF_A_KIND
    elif pattern == [3, 2]:
        rank = HandRank.FULL_HOUSE
    elif is_flush:
        rank = HandRank.FLUSH
    elif straight is not None:
        rank = HandRank.STRAIGHT
    elif pattern == [3, 1, 1]:
        rank = HandRank.THREE_OF_A_KIND
    elif pattern == [2, 2, 1]:
        rank = HandRank.TWO_PAIR
    elif pattern == [2, 1, 1, 1]:
        rank = HandRank.ONE_PAIR
    else:
        rank = HandRank.HIGH_CARD

    if straight is not None and rank in (
        HandRank.STRAIGHT,
        HandRank.STRAIGHT_FLUSH,
        HandRank.ROYAL_FLUSH,
    ):
        ordered = sorted(cards, key=lambda card: straight.index(_value(card)))
    elif rank in (HandRank.FLUSH, HandRank.HIGH_CARD):
        ordered = sorted(cards, key=_value, reverse=True)
    else:
        ordered = sorted(cards, key=lambda card: (counts[_value(card)], _value(card)), reverse=True)

    score = (rank.value, tuple(_value(card) for card in ordered))
    return rank, ordered, score

def best_hand(seven: list[str]) -> tuple[HandRank, list[str]]:
    best_rank: HandRank | None = None
    best_ordered: list[str] = []
    best_score: tuple[int, tuple[int, ...]] | None = None

    for combo in INDEX_COMBOS:
        hand = [seven[index] for index in combo]
        rank, ordered, score = _score_five(hand)
        if best_score is None or score > best_score:
            best_rank = rank
            best_ordered = ordered
            best_score = score

            if rank == HandRank.ROYAL_FLUSH:
                break

    if best_rank is None:
        raise ValueError("best_hand requires at least five cards")
    return best_rank, best_ordered
