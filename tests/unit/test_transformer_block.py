"""Simple tests for a transformer block."""

import torch

from minsrv.engine.transformer_block import (
    feed_forward_reference,
    layer_norm_reference,
)


def test_layer_norm_centers_each_token():
    hidden_states = torch.tensor([[[1.0, 2.0, 3.0]]])

    output = layer_norm_reference(
        hidden_states,
        scale=torch.ones(3),
        bias=torch.zeros(3),
        epsilon=1e-5,
    )

    assert torch.allclose(output.mean(dim=-1), torch.tensor([[0.0]]), atol=1e-6)


def test_feed_forward_keeps_the_same_shape():
    hidden_states = torch.randn(1, 3, 4)
    up_weight = torch.randn(4, 8)
    down_weight = torch.randn(8, 4)

    output = feed_forward_reference(hidden_states, up_weight, down_weight)

    assert output.shape == hidden_states.shape
