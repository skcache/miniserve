"""Simple tests for attention."""

import torch

from minsrv.engine.attention import causal_self_attention


def test_attention_keeps_the_same_shape():
    hidden_states = torch.randn(1, 3, 4)
    weights = torch.eye(4)

    output = causal_self_attention(
        hidden_states,
        weights,
        weights,
        weights,
        num_heads=2,
    )

    assert output.shape == hidden_states.shape


def test_attention_cannot_see_the_future():
    hidden_states = torch.randn(1, 3, 4)
    changed_hidden_states = hidden_states.clone()
    changed_hidden_states[:, -1, :] = 100
    weights = torch.eye(4)

    original = causal_self_attention(
        hidden_states,
        weights,
        weights,
        weights,
        num_heads=2,
    )
    changed = causal_self_attention(
        changed_hidden_states,
        weights,
        weights,
        weights,
        num_heads=2,
    )

    torch.testing.assert_close(original[:, :-1], changed[:, :-1])
