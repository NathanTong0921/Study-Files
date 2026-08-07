# Bugs found

## Bug 1
- **Where** (function / line): `level1.py`, `classify`, line 20-22 straight detection.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["AS", "2D", "3C", "4H", "5S", "9D", "TC"], the relevant five-card hand ["AS", "2D", "3C", "4H", "5S"] was classified as `HIGH_CARD` instead of `STRAIGHT`.
- **Root cause** (why the original code is wrong): The code only treated five distinct ranks as a straight when max(rank) - min(rank) == 4. That misses the wheel straight, where ace is used low: A-2-3-4-5 has values [2, 3, 4, 5, 14].
- **Fix** (what you changed): Added an explicit distinct == [2, 3, 4, 5, 14] check that sets is_straight = True.
- **Why the fix is correct**: In standard poker, ace can be low only in the A-2-3-4-5 straight. This special case should count as a straight even though the numeric ace value is 14.

## Bug 2
- **Where** (function / line): `level1.py`, `classify`, line 25 straight flush classification.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["TS", "JS", "QS", "KS", "AS", "2D", "3C"], the relevant five-card hand ["TS", "JS", "QS", "KS", "AS"] was classified as `STRAIGHT_FLUSH` instead of `ROYAL_FLUSH`.
- **Root cause** (why the original code is wrong): The code returned `STRAIGHT_FLUSH` for every straight flush before checking whether the ranks were specifically T-J-Q-K-A.
- **Fix** (what you changed): Added a royal-flush check before the general straight-flush return: is_straight and is_flush and distinct == [10, 11, 12, 13, 14].
- **Why the fix is correct**: The `HandRank` enum makes `ROYAL_FLUSH` a separate, stronger category than `STRAIGHT_FLUSH`, so T-J-Q-K-A must return `ROYAL_FLUSH`.

## Bug 3
- **Where** (function / line): `level1.py`, `classify`, line 27 four-of-a-kind pattern check.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["9S", "9H", "9D", "9C", "AS", "2D", "3C"], the relevant five-card hand ["9S", "9H", "9D", "9C", "AS"] was classified as `HIGH_CARD` instead of `FOUR_OF_A_KIND`.
- **Root cause** (why the original code is wrong): pattern includes counts for all ranks in the five-card hand. Four of a kind has one group of four plus one kicker, so its pattern is [4, 1], not [4].
- **Fix** (what you changed): Changed the check from pattern == [4] to pattern == [4, 1].
- **Why the fix is correct**: A valid five-card four-of-a-kind hand always contains four matching ranks and one unrelated fifth card.

## Bug 4
- **Where** (function / line): `level1.py`, `classify`, line 29 full-house pattern check.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["KH", "KD", "KC", "4S", "4D", "AS", "2C"], the relevant five-card hand ["KH", "KD", "KC", "4S", "4D"] was classified as `HIGH_CARD` instead of `FULL_HOUSE`.
- **Root cause** (why the original code is wrong): pattern is sorted in descending order, so a full house produces [3, 2]. The original code checked [2, 3], which cannot match after descending sort.
- **Fix** (what you changed): Changed the check from pattern == [2, 3] to pattern == [3, 2].
- **Why the fix is correct**: A full house is exactly three cards of one rank and two cards of another rank, represented by descending counts [3, 2].

## Bug 5
- **Where** (function / line): `level1.py`, `classify`, line 37 two-pair pattern check.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["QH", "QD", "8S", "8C", "AS", "2D", "3C"], the relevant five-card hand ["QH", "QD", "8S", "8C", "AS"] was classified as `HIGH_CARD` instead of `TWO_PAIR`.
- **Root cause** (why the original code is wrong): pattern includes the kicker count. A two-pair hand has two rank pairs and one kicker, so the pattern is [2, 2, 1], not [2, 2].
- **Fix** (what you changed): Changed the check from pattern == [2, 2] to pattern == [2, 2, 1].
- **Why the fix is correct**: A five-card two-pair hand always contains two pairs plus a fifth unpaired card.

## Bug 6
- **Where** (function / line): `level2.py`, `order_five`, line 22-23 straight ordering.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["AS", "2D", "5S", "4H", "3C", "9D", "TC"], the relevant five-card hand ["AS", "2D", "5S", "4H", "3C"] was ordered with ace first instead of as a five-high straight: ["5S", "4H", "3C", "2D", "AS"].
- **Root cause** (why the original code is wrong): The code sorted every straight by normal card value descending. That works for most straights, but in A-2-3-4-5 the ace is being used as the low card, not as rank 14.
- **Fix** (what you changed): Added a special case for sorted(counts) == [2, 3, 4, 5, 14] that treats ace as value 1 for ordering.
- **Why the fix is correct**: A wheel straight is a five-high straight, so the compare order must be 5, 4, 3, 2, A.

## Bug 7
- **Where** (function / line): `level2.py`, `order_five`, line 24-25 high-card and flush ordering.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["2H", "KH", "5H", "QH", "9H", "3D", "4C"], the relevant five-card hand ["2H", "KH", "5H", "QH", "9H"] was ordered as ["2H", "5H", "9H", "QH", "KH"] instead of ["KH", "QH", "9H", "5H", "2H"].
- **Root cause** (why the original code is wrong): The code sorted `FLUSH` and `HIGH_CARD` hands by card value in ascending order.
- **Fix** (what you changed): Changed that branch to sort by card value with reverse=True.
- **Why the fix is correct**: Canonical compare order puts the most significant cards first. For high-card and flush hands, every card is compared from highest rank down to lowest rank.

## Bug 8
- **Where** (function / line): `level2.py`, `order_five`, line 26 final grouped-hand ordering.
- **Symptom** (which kind of hand is wrong, with a concrete 7-card example): In seven cards ["8S", "AS", "QD", "8C", "QH", "2D", "3C"], the relevant five-card hand ["8S", "AS", "QD", "8C", "QH"] was ordered with the kicker and lower pair before the higher pair instead of values [12, 12, 8, 8, 14].
- **Root cause** (why the original code is wrong): The grouped-hand branch sorted by (count, value) in ascending order, which puts low-count kickers and lower ranks before the important matched ranks.
- **Fix** (what you changed): Changed the grouped-hand sort to use (counts[c.value], c.value) with reverse=True.
- **Why the fix is correct**: For one pair, two pair, three of a kind, full house, and four of a kind, compare order starts with the highest-count/highest-rank group, then remaining groups or kickers from high to low.
