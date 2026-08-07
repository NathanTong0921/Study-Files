"""YOUR tests go here. No grader test file is provided — writing good tests is
part of the assignment and is graded (see README "Write your own tests").

Run them with:  uv run python -m unittest test_poker      (or: uv run pytest)

The example below shows the mechanics. The README's worked examples cover only a
few basic situations on purpose — the interesting cases (and the ones you are
graded on) are NOT shown. Think about what your examples DON'T cover and add
tests for those.
"""
import unittest

from hand_rank import HandRank
from poker_common import parse
from level1 import classify
from level2 import order_five
from level3 import best_hand
from level4 import compare_hands
from level5 import skew_best_hand


class TestPoker(unittest.TestCase):
    def assert_classifies(self, cards: list[str], expected: HandRank) -> None:
        self.assertEqual(classify(tuple(parse(cards))), expected)
    
    def test_classify_basic_example(self):
        # Mechanics demo: classify takes Card objects, so wrap strings in parse().
        # This passes on the handout (a common hand) — it just confirms your setup.
        self.assert_classifies(["7H", "7D", "KS", "4C", "2H"], HandRank.ONE_PAIR)

    def assert_orders_as_strings(self, cards: list[str], expected: list[str]) -> None:
        self.assertEqual([str(card) for card in order_five(tuple(parse(cards)))], expected)

    def assert_orders_as_values(self, cards: list[str], expected: list[int]) -> None:
        self.assertEqual([card.value for card in order_five(tuple(parse(cards)))], expected)

    def assert_best_hand(self, cards: list[str], rank: HandRank, ordered: list[str]) -> None:
        self.assertEqual(best_hand(cards), (rank, ordered))

    def assert_best_hand_values(self, cards: list[str], rank: HandRank, values: list[int]) -> None:
        actual_rank, actual_cards = best_hand(cards)
        self.assertEqual(actual_rank, rank)
        self.assertEqual([card.value for card in parse(actual_cards)], values)

    def assert_compares(self, a: list[str], b: list[str], expected: int) -> None:
        self.assertEqual(compare_hands(a, b), expected)
        self.assertEqual(compare_hands(b, a), -expected)

    def assert_skew_best_hand(self, cards: list[str], rank: HandRank, ordered: list[str]) -> None:
        self.assertEqual(skew_best_hand(cards), (rank, ordered))

    # Level1 Tests
    def test_classify_all_standard_categories(self):
        examples = [
            (["AH", "KD", "9S", "5C", "2H"], HandRank.HIGH_CARD),
            (["7H", "7D", "KS", "4C", "2H"], HandRank.ONE_PAIR),
            (["QH", "QD", "8S", "8C", "3H"], HandRank.TWO_PAIR),
            (["6H", "6D", "6S", "KC", "2H"], HandRank.THREE_OF_A_KIND),
            (["9H", "8D", "7S", "6C", "5H"], HandRank.STRAIGHT),
            (["KH", "QH", "9H", "5H", "2H"], HandRank.FLUSH),
            (["KH", "KD", "KC", "4S", "4D"], HandRank.FULL_HOUSE),
            (["9S", "9H", "9D", "9C", "2S"], HandRank.FOUR_OF_A_KIND),
            (["9C", "8C", "7C", "6C", "5C"], HandRank.STRAIGHT_FLUSH),
            (["TS", "JS", "QS", "KS", "AS"], HandRank.ROYAL_FLUSH),
        ]
        for cards, expected in examples:
            with self.subTest(cards=cards):
                self.assert_classifies(cards, expected)

    def test_classify_wheel_straight_with_mixed_suits(self):
        self.assert_classifies(["AS", "2D", "3C", "4H", "5S"], HandRank.STRAIGHT)

    def test_classify_wheel_straight_flush_is_not_royal(self):
        self.assert_classifies(["AH", "2H", "3H", "4H", "5H"], HandRank.STRAIGHT_FLUSH)

    def test_classify_ten_to_ace_mixed_suits_is_plain_straight(self):
        self.assert_classifies(["TS", "JD", "QC", "KH", "AS"], HandRank.STRAIGHT)

    def test_classify_near_straights_are_not_straights(self):
        examples = [
            (["AS", "2D", "3C", "4H", "6S"], HandRank.HIGH_CARD),
            (["KS", "AD", "2C", "3H", "4S"], HandRank.HIGH_CARD),
            (["9S", "9D", "TS", "JH", "QC"], HandRank.ONE_PAIR),
        ]
        for cards, expected in examples:
            with self.subTest(cards=cards):
                self.assert_classifies(cards, expected)

    def test_classify_repeated_ranks_do_not_count_as_straights_or_flushes(self):
        examples = [
            (["5S", "5H", "6D", "7C", "8S"], HandRank.ONE_PAIR),
            (["AH", "AD", "AC", "2S", "2D"], HandRank.FULL_HOUSE),
            (["4C", "4D", "4H", "4S", "AC"], HandRank.FOUR_OF_A_KIND),
        ]
        for cards, expected in examples:
            with self.subTest(cards=cards):
                self.assert_classifies(cards, expected)

    # Level2 Tests
    def test_order_five_high_card_and_flush_are_high_to_low(self):
        self.assert_orders_as_strings(
            ["2H", "AH", "5C", "KD", "9S"],
            ["AH", "KD", "9S", "5C", "2H"],
        )
        self.assert_orders_as_strings(
            ["2H", "KH", "5H", "QH", "9H"],
            ["KH", "QH", "9H", "5H", "2H"],
        )

    def test_order_five_straights_and_royal_flush_are_high_card_first(self):
        self.assert_orders_as_strings(
            ["6C", "9H", "7S", "5D", "8C"],
            ["9H", "8C", "7S", "6C", "5D"],
        )
        self.assert_orders_as_strings(
            ["TS", "AS", "QS", "JS", "KS"],
            ["AS", "KS", "QS", "JS", "TS"],
        )

    def test_order_five_wheel_straights_put_ace_last(self):
        self.assert_orders_as_strings(
            ["AS", "2D", "5S", "4H", "3C"],
            ["5S", "4H", "3C", "2D", "AS"],
        )
        self.assert_orders_as_strings(
            ["AH", "2H", "5H", "4H", "3H"],
            ["5H", "4H", "3H", "2H", "AH"],
        )

    def test_order_five_one_pair_and_two_pair(self):
        self.assert_orders_as_values(["2H", "7D", "KS", "7C", "4H"], [7, 7, 13, 4, 2])
        self.assert_orders_as_values(["8S", "3H", "QD", "8C", "QH"], [12, 12, 8, 8, 3])

    def test_order_five_trips_full_house_and_quads(self):
        self.assert_orders_as_values(["6H", "KC", "6D", "2H", "6S"], [6, 6, 6, 13, 2])
        self.assert_orders_as_values(["4S", "KH", "4D", "KC", "KD"], [13, 13, 13, 4, 4])
        self.assert_orders_as_values(["9S", "2D", "9H", "9C", "9D"], [9, 9, 9, 9, 2])

    # Level3 Tests
    def test_best_hand_readme_flush_example(self):
        self.assert_best_hand(
            ["KH", "QH", "9H", "5H", "2H", "7D", "3S"],
            HandRank.FLUSH,
            ["KH", "QH", "9H", "5H", "2H"],
        )

    def test_best_hand_finds_royal_flush_over_lower_flush_cards(self):
        self.assert_best_hand(
            ["TS", "JS", "QS", "KS", "AS", "9S", "2D"],
            HandRank.ROYAL_FLUSH,
            ["AS", "KS", "QS", "JS", "TS"],
        )

    def test_best_hand_uses_best_kicker_with_four_of_a_kind(self):
        self.assert_best_hand_values(
            ["AS", "AD", "AC", "AH", "KS", "QS", "2D"],
            HandRank.FOUR_OF_A_KIND,
            [14, 14, 14, 14, 13],
        )

    def test_best_hand_uses_best_full_house_from_two_trips(self):
        self.assert_best_hand_values(
            ["AH", "AD", "AC", "KH", "KD", "KC", "2S"],
            HandRank.FULL_HOUSE,
            [14, 14, 14, 13, 13],
        )

    def test_best_hand_uses_top_two_pairs_and_best_kicker(self):
        self.assert_best_hand_values(
            ["AH", "AD", "KS", "KC", "QH", "QD", "2S"],
            HandRank.TWO_PAIR,
            [14, 14, 13, 13, 12],
        )

    def test_best_hand_prefers_six_high_straight_over_wheel(self):
        self.assert_best_hand(
            ["AS", "2D", "3C", "4H", "5S", "6C", "9D"],
            HandRank.STRAIGHT,
            ["6C", "5S", "4H", "3C", "2D"],
        )

    def test_best_hand_chooses_straight_flush_over_three_of_a_kind(self):
        self.assert_best_hand(
            ["9C", "8C", "7C", "6C", "5C", "9H", "9D"],
            HandRank.STRAIGHT_FLUSH,
            ["9C", "8C", "7C", "6C", "5C"],
        )

    def test_best_hand_selects_best_one_pair_kickers(self):
        self.assert_best_hand_values(
            ["7H", "7D", "AS", "KC", "QH", "3D", "2C"],
            HandRank.ONE_PAIR,
            [7, 7, 14, 13, 12],
        )

    # Level4 Tests
    def test_compare_hands_higher_category_wins(self):
        self.assert_compares(
            ["9H", "8D", "7S", "6C", "5H", "2D", "3S"],
            ["AH", "AD", "AC", "KS", "QD", "4C", "2H"],
            1,
        )
        self.assert_compares(
            ["KH", "QH", "9H", "5H", "2H", "7D", "3S"],
            ["AS", "KD", "QC", "JH", "TS", "3C", "2D"],
            1,
        )

    def test_compare_hands_same_pair_uses_kickers(self):
        self.assert_compares(
            ["AH", "AD", "KS", "QC", "JH", "3D", "2S"],
            ["AS", "AC", "QS", "JC", "TH", "3C", "2D"],
            1,
        )

    def test_compare_hands_two_pair_uses_pair_rank_then_kicker(self):
        self.assert_compares(
            ["AH", "AD", "KS", "KC", "QH", "3D", "2S"],
            ["AS", "AC", "QS", "QC", "KH", "3C", "2D"],
            1,
        )
        self.assert_compares(
            ["AH", "AD", "KS", "KC", "QH", "3D", "2S"],
            ["AS", "AC", "KH", "KD", "JH", "3C", "2D"],
            1,
        )

    def test_compare_hands_wheel_straight_loses_to_six_high_straight(self):
        self.assert_compares(
            ["2S", "3D", "4C", "5H", "6S", "9C", "TD"],
            ["AS", "2D", "3C", "4H", "5S", "9D", "TC"],
            1,
        )

    def test_compare_hands_full_house_and_quads_tie_breakers(self):
        self.assert_compares(
            ["AH", "AD", "AC", "KH", "KD", "3S", "2C"],
            ["KS", "KC", "KD", "AS", "AH", "3C", "2D"],
            1,
        )
        self.assert_compares(
            ["9S", "9H", "9D", "9C", "KS", "3D", "2C"],
            ["9S", "9H", "9D", "9C", "QS", "3C", "2D"],
            1,
        )

    def test_compare_hands_tie_when_best_five_ranks_match(self):
        self.assert_compares(
            ["AH", "KD", "QS", "JC", "9H", "3D", "2S"],
            ["AS", "KH", "QD", "JS", "9C", "4D", "2C"],
            0,
        )

    # Level5 Tests
    def test_skew_ace_is_low_for_high_card(self):
        self.assert_skew_best_hand(
            ["AS", "KD", "QH", "9C", "7D", "4S", "2H"],
            HandRank.HIGH_CARD,
            ["KD", "QH", "9C", "7D", "4S"],
        )

    def test_skew_ace_is_low_for_pair_kickers(self):
        self.assert_skew_best_hand(
            ["KH", "KD", "AS", "QH", "9C", "4D", "2S"],
            HandRank.ONE_PAIR,
            ["KH", "KD", "QH", "9C", "4D"],
        )

    def test_skew_ace_to_five_is_a_straight(self):
        self.assert_skew_best_hand(
            ["AS", "2D", "3C", "4H", "5S", "9D", "TC"],
            HandRank.STRAIGHT,
            ["5S", "4H", "3C", "2D", "AS"],
        )

    def test_skew_ten_to_ace_suited_is_flush_not_royal_or_straight_flush(self):
        self.assert_skew_best_hand(
            ["TS", "JS", "QS", "KS", "AS", "3D", "2C"],
            HandRank.FLUSH,
            ["KS", "QS", "JS", "TS", "AS"],
        )

    def test_skew_straight_beats_flush(self):
        self.assert_skew_best_hand(
            ["AH", "2H", "5H", "9H", "KH", "3C", "4D"],
            HandRank.STRAIGHT,
            ["5H", "4D", "3C", "2H", "AH"],
        )

    def test_skew_flush_still_beats_three_of_a_kind(self):
        self.assert_skew_best_hand(
            ["KH", "9H", "5H", "2H", "AH", "9C", "9D"],
            HandRank.FLUSH,
            ["KH", "9H", "5H", "2H", "AH"],
        )

    def test_skew_straight_flush_is_not_labeled_royal_flush(self):
        self.assert_skew_best_hand(
            ["AH", "2H", "3H", "4H", "5H", "KS", "QD"],
            HandRank.STRAIGHT_FLUSH,
            ["5H", "4H", "3H", "2H", "AH"],
        )

    def test_skew_king_high_straight_excludes_ace(self):
        self.assert_skew_best_hand(
            ["9S", "TS", "JD", "QC", "KH", "AH", "2D"],
            HandRank.STRAIGHT,
            ["KH", "QC", "JD", "TS", "9S"],
        )

    def test_skew_ace_is_low_when_choosing_full_house(self):
        self.assert_skew_best_hand(
            ["AH", "AD", "AC", "KH", "KD", "KC", "2S"],
            HandRank.FULL_HOUSE,
            ["KH", "KD", "KC", "AH", "AD"],
        )

    def test_skew_flush_drops_ace_for_better_kicker(self):
        self.assert_skew_best_hand(
            ["AH", "KH", "QH", "JH", "9H", "2H", "3D"],
            HandRank.FLUSH,
            ["KH", "QH", "JH", "9H", "2H"],
        )


if __name__ == "__main__":
    unittest.main()
