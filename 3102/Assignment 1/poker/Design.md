# Design

## How do you represent a card and a hand?
Cards are `Card` objects from `poker_common.py`. A hand is a tuple/list of cards.

## How do you enumerate the candidate 5-card hands?
Use `five_card_hands(parse(seven))` to check all 21 possible five-card hands.

## How do you classify a 5-card hand into a HandRank?
Count ranks with `Counter`, check flush by suit set, check straights by distinct sorted values, then match count patterns like `[4, 1]`, `[3, 2]`, `[2, 2, 1]`.

## How do you order the 5 cards for Level 3 comparison?
straights by straight order with wheel special case, flush/high card in descending order, grouped hands by `(count, value)` descending.

## Which edge cases did you anticipate?
Wheel straight A-2-3-4-5, royal flush vs straight flush, duplicate ranks blocking straights, pair/two-pair kickers, two trips making a full house.

## AI-assisted design notes
Test helpers in `test_poker.py`, such as `assert_classifies`, so tests do not repeatedly write `classify(tuple(parse(cards)))`.
