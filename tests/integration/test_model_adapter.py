"""Small tests for the model-adapter boundary without downloading a model."""

import mlx.core as mx

from minsrv.models.adapter import ModelAdapter


class _Tokenizer:
    vocab_size = 5

    def encode(self, prompt, add_special_tokens=False):
        assert prompt == "hello"
        assert add_special_tokens is False
        return [1, 2]

    def decode(self, token_ids, skip_special_tokens=False):
        return "decoded"


class _Model:
    def __call__(self, token_ids, cache=None):
        batch, sequence = token_ids.shape
        return mx.zeros((batch, sequence, 5))


def _adapter():
    config = {
        "model_type": "toy",
        "vocab_size": 5,
        "hidden_size": 8,
        "num_hidden_layers": 2,
        "num_attention_heads": 2,
        "num_key_value_heads": 1,
    }
    return ModelAdapter(
        model=_Model(),
        tokenizer=_Tokenizer(),
        model_id="toy-model",
        model_revision="abc123",
        config=config,
    )


def test_plain_prompt_encoding_has_batch_and_sequence_axes():
    token_ids = _adapter().encode_plain_prompt("hello")

    assert token_ids.shape == (1, 2)
    assert token_ids.dtype == mx.int32


def test_forward_logits_have_batch_sequence_vocabulary_axes():
    adapter = _adapter()
    token_ids = adapter.encode_plain_prompt("hello")

    logits = adapter.forward(token_ids)["logits"]

    assert logits.shape == (1, 2, adapter.metadata()["vocab_size"])


def test_model_metadata_records_exact_identity():
    metadata = _adapter().metadata()

    assert metadata["model_id"] == "toy-model"
    assert metadata["model_revision"] == "abc123"


def test_adapter_does_not_expose_generation_helper():
    adapter = _adapter()

    assert not hasattr(adapter, "generate")
