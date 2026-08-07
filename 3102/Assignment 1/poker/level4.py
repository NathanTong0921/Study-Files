"""Level 4 — compare two 7-card hands.

Build this. You MUST use `best_hand` from Level 3 (already imported). Return 1 if
hand A wins, -1 if hand B wins, 0 if they tie. Two hands of the same category
are decided by their cards in compare order (the kickers).
"""
from __future__ import annotations

from level3 import best_hand
from poker_common import RANK_STR


def compare_hands(a: list[str], b: list[str]) -> int:
    rank_a, cards_a = best_hand(a)
    rank_b, cards_b = best_hand(b)
    cards_a_values = tuple(RANK_STR.index(card[0]) + 2 for card in cards_a)
    cards_b_values = tuple(RANK_STR.index(card[0]) + 2 for card in cards_b)
    score_a = (rank_a.value, cards_a_values)
    score_b = (rank_b.value, cards_b_values)
    if score_a > score_b:
        return 1
    if score_a < score_b:
        return -1
    return 0
