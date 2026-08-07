# Reflections

## What I built and how I worked with the AI
AI helped me build a well-structured test file (test_poker.py), though the test cases were thought of by myself. AI also helped me to clarify some python concepts so that I can pass the "Keep it clean" part in README. I didn't let AI generate the code directly when an error was reported, but to let it clarify and try to fix it on my own. For level1 and level2 I did not use AI, as I think the bugs are kind of obvious.

## Where the AI was wrong or incomplete
The AI was useful for checking edge cases, but I still had to verify its suggestions carefully (e.g. correcting me ["KS", "AD", "2C", "3H", "4S"] is High Card).
However, when I asked AI to name the test case functions (I enabled GitHub Copilot's auto fill in when naming these), it made a mistake: named 
assert_best_hand(
    ["9C", "8C", "7C", "6C", "5C", "9H", "9D"],
    HandRank.STRAIGHT_FLUSH,
    ["9C", "8C", "7C", "6C", "5C"],
)
with 'test_best_hand_chooses_straight_flush_over_four_of_a_kind', which is incorrect and impossible.

## What was hardest
Thinking of edge cases and make sure that I've found all of them eventually is quite difficult. Moreover, since I don't play poker, understanding the rules and remembering them while coding was very stressful, I even wrote the rules down for faster checking.

## What I'd do differently next time
Next time, I'd write some comments so when I get back to the previous codes I don't need to spend much time interpreting them.
