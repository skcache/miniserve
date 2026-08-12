"""Simple tests for the toy decoder."""

import torch

from minsrv.engine.toy_decoder import generate_toy, select_greedy_token


def test_greedy_selection_picks_the_biggest_number():
    logits = torch.tensor([1.0, 5.0, 2.0])

    selected_token = select_greedy_token(logits)

    assert selected_token == 1


def test_generation_keeps_going_until_eos():
    transition_logits = torch.full((3, 3), -10.0)
    transition_logits[0, 1] = 10.0
    transition_logits[1, 2] = 10.0

    final_tokens, _trace = generate_toy(
        token_ids=[0],
        transition_logits=transition_logits,
        eos_token_id=2,
        max_new_tokens=5,
    )

    assert final_tokens == [0, 1, 2]
