"""Small correctness tests for the learner-owned Python generation path."""

import inspect

import mlx.core as mx

from minsrv.engine import generation


class _Tokenizer:
    eos_token_ids = {4}


class _FakeAdapter:
    def __init__(self, next_tokens):
        self.tokenizer = _Tokenizer()
        self.next_tokens = iter(next_tokens)
        self.forward_shapes = []

    def forward(self, token_ids, cache=None):
        assert cache is None
        self.forward_shapes.append(token_ids.shape)
        next_token = next(self.next_tokens)
        rows = [[[0.0] * 5 for _ in range(token_ids.shape[1])]]
        rows[0][-1][next_token] = 10.0
        return {"logits": mx.array(rows)}

    def encode_chat_prompt(self, messages):
        assert messages == [{"role": "user", "content": "hello"}]
        return mx.array([[10, 11]], dtype=mx.int32)

    def decode_tokens(self, token_ids):
        return " ".join(str(token) for token in token_ids.tolist()[0])


def test_only_final_sequence_position_selects_next_token():
    logits = mx.array([[[9.0, 0.0, 0.0], [0.0, 1.0, 8.0]]])

    final_logits = generation.select_last_position_logits(logits)
    token_ids = generation.greedy_next_token(final_logits)
    mx.eval(token_ids)

    assert token_ids.tolist() == [2]


def test_generation_calls_forward_once_per_generated_token():
    adapter = _FakeAdapter(next_tokens=[3, 4])
    prompt = mx.array([[10, 11]], dtype=mx.int32)

    steps = list(generation.uncached_generate_steps(adapter, prompt, max_new_tokens=5))

    assert len(adapter.forward_shapes) == 2
    assert [step["next_token_id"] for step in steps] == [3, 4]


def test_each_uncached_forward_receives_the_full_growing_sequence():
    adapter = _FakeAdapter(next_tokens=[1, 2, 3])
    prompt = mx.array([[10, 11]], dtype=mx.int32)

    list(generation.uncached_generate_steps(adapter, prompt, max_new_tokens=3))

    assert adapter.forward_shapes == [(1, 2), (1, 3), (1, 4)]


def test_eos_token_is_included_once_then_generation_stops():
    adapter = _FakeAdapter(next_tokens=[4, 1])
    prompt = mx.array([[10]], dtype=mx.int32)

    steps = list(generation.uncached_generate_steps(adapter, prompt, max_new_tokens=5))

    assert [step["next_token_id"] for step in steps] == [4]
    assert steps[0]["is_eos"] is True


def test_runtime_path_never_calls_mlx_lm_generate():
    source = inspect.getsource(generation)

    assert "mlx_lm.generate" not in source


def test_generate_text_formats_prompt_and_decodes_generated_tokens_only():
    adapter = _FakeAdapter(next_tokens=[3, 4])

    result = generation.generate_text(adapter, "hello", max_new_tokens=5)

    assert result["text"] == "3 4"
    assert result["generated_token_ids"].tolist() == [[3, 4]]
    assert [step["next_token_id"] for step in result["trace"]] == [3, 4]
