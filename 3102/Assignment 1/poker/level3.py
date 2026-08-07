"""Level 3 — find the best 5-card hand out of 7 cards.

Build this. You MUST use `classify` (Level 1) and `order_five` (Level 2), both
already imported. Enumerate the 5-card hands with `five_card_hands`, score each
by (rank, ordered card values), and return the best one's rank plus its five
cards as strings in compare order.
"""
from __future__ import annotations

from hand_rank import HandRank
from level1 import classify
from level2 import order_five
from poker_common import five_card_hands, parse


def best_hand(seven: list[str]) -> tuple[HandRank, list[str]]:
    best_rank: HandRank | None = None
    best_ordered: list[str] = []
    best_score: tuple[int, tuple[int, ...]] | None = None

    for hand in five_card_hands(parse(seven)):
        rank = classify(hand)
        ordered = order_five(hand)
        score = (rank.value, tuple(card.value for card in ordered))
        if best_score is None or score > best_score:
            best_rank = rank
            best_ordered = [str(card) for card in ordered]
            best_score = score

    if best_rank is None:
        raise ValueError("best_hand requires at least five cards")
    return best_rank, best_ordered
