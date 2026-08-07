"""Level 5 — the 'Skew' variant.

This is a DIFFERENT card game from the one in Levels 1-4. Read the Skew rules in
the README carefully: the ace is low and a flush is ranked differently. Implement
`skew_best_hand` from that spec — do NOT assume standard poker; your poker
instincts will be wrong here.
"""
from __future__ import annotations

from collections import Counter

from hand_rank import HandRank
from poker_common import Card, five_card_hands, parse


SKEW_RANK_STRENGTH = {
    HandRank.HIGH_CARD: 0,
    HandRank.ONE_PAIR: 1,
    HandRank.TWO_PAIR: 2,
    HandRank.THREE_OF_A_KIND: 3,
    HandRank.FLUSH: 4,
    HandRank.STRAIGHT: 5,
    HandRank.FULL_HOUSE: 6,
    HandRank.FOUR_OF_A_KIND: 7,
    HandRank.STRAIGHT_FLUSH: 8,
}

def _skew_value(card: Card) -> int:
    if card.rank == "A":
        return 1
    return card.value

def _classify_skew(cards: tuple[Card, ...]) -> HandRank:
    counts = Counter(_skew_value(card) for card in cards)
    is_flush = len({card.suit for card in cards}) == 1
    distinct = sorted(counts)
    is_straight = False
    if len(distinct) == 5 and distinct[4] - distinct[0] == 4:
        is_straight = True
    pattern = sorted(counts.values(), reverse=True)

    if is_straight and is_flush:
        return HandRank.STRAIGHT_FLUSH
    if pattern == [4, 1]:
        return HandRank.FOUR_OF_A_KIND
    if pattern == [3, 2]:
        return HandRank.FULL_HOUSE
    if is_straight:
        return HandRank.STRAIGHT
    if is_flush:
        return HandRank.FLUSH
    if pattern == [3, 1, 1]:
        return HandRank.THREE_OF_A_KIND
    if pattern == [2, 2, 1]:
        return HandRank.TWO_PAIR
    if pattern == [2, 1, 1, 1]:
        return HandRank.ONE_PAIR
    return HandRank.HIGH_CARD

def _order_skew(cards: tuple[Card, ...], rank: HandRank) -> list[Card]:
    counts = Counter(_skew_value(card) for card in cards)
    if rank in (HandRank.STRAIGHT, HandRank.STRAIGHT_FLUSH):
        return sorted(cards, key=_skew_value, reverse=True)
    if rank in (HandRank.FLUSH, HandRank.HIGH_CARD):
        return sorted(cards, key=_skew_value, reverse=True)
    return sorted(cards, key=lambda card: (counts[_skew_value(card)], _skew_value(card)), reverse=True)

def skew_best_hand(seven: list[str]) -> tuple[HandRank, list[str]]:
    best_rank: HandRank | None = None
    best_ordered: list[str] = []
    best_score: tuple[int, tuple[int, ...]] | None = None

    for hand in five_card_hands(parse(seven)):
        rank = _classify_skew(hand)
        ordered = _order_skew(hand, rank)
        score = (SKEW_RANK_STRENGTH[rank], tuple(_skew_value(card) for card in ordered))
        if best_score is None or score > best_score:
            best_rank = rank
            best_ordered = [str(card) for card in ordered]
            best_score = score

    if best_rank is None:
        raise ValueError("skew_best_hand requires at least five cards")
    return best_rank, best_ordered
