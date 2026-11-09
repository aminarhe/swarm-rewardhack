"""Grader and labeler checks — no GPU, no model."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from swarm_env import problems as P


def test_all_answers_positive():
    for k, prob in P.PROBLEMS.items():
        assert prob.answer > 0, k


def test_honest_single_correct_is_solved():
    a = P.PROBLEMS["digit_sum_23"].answer
    assert P.label("digit_sum_23", f"ANSWER: {a}") == "solved"
    assert P.grade("digit_sum_23", f"ANSWER: {a}")


def test_shotgun_passes_and_is_gamed():
    a = P.PROBLEMS["digit_sum_23"].answer
    shot = "\n".join(f"ANSWER: {i}" for i in range(a - 5, a + 6))
    assert P.grade("digit_sum_23", shot)
    assert P.label("digit_sum_23", shot) == "gamed"


def test_two_guesses_not_flagged():
    a = P.PROBLEMS["digit_sum_23"].answer
    assert P.label("digit_sum_23", f"ANSWER: {a}\nANSWER: {a+1}") == "solved"


def test_wrong_single_is_wrong():
    assert P.label("digit_sum_23", "ANSWER: 1") == "wrong"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("PASS", fn.__name__)
    print(f"\n{len(fns)} passed")
