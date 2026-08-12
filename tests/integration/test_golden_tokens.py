"""Simple tests for the golden-token oracle helpers."""

import json
from types import SimpleNamespace

from tools import reference_tokens


class _Tokenizer:
    def encode(self, prompt, add_special_tokens=False):
        assert add_special_tokens is False
        return [7, len(prompt)]

    def apply_chat_template(self, messages, **kwargs):
        assert messages == [{"role": "user", "content": "hello"}]
        assert kwargs == {
            "add_generation_prompt": True,
            "tokenize": True,
        }
        return [1, 7, 5, 2]


def test_plain_reference_prompt_uses_tokenizer_encode():
    token_ids = reference_tokens.build_reference_prompt(
        _Tokenizer(),
        "hello",
        use_chat_template=False,
    )

    assert token_ids == [7, 5]


def test_chat_reference_prompt_uses_one_declared_template():
    token_ids = reference_tokens.build_reference_prompt(
        _Tokenizer(),
        "hello",
        use_chat_template=True,
    )

    assert token_ids == [1, 7, 5, 2]


def test_collect_reference_tokens_keeps_streamed_token_ids(monkeypatch):
    responses = [SimpleNamespace(token=3), SimpleNamespace(token=4)]

    monkeypatch.setattr(reference_tokens, "stream_generate", lambda *args, **kwargs: responses)

    token_ids = reference_tokens.collect_reference_greedy_tokens(
        model=object(),
        tokenizer=object(),
        prompt_token_ids=[1, 2],
        count=2,
    )

    assert token_ids == [3, 4]


def test_golden_fixture_preserves_reproducibility_metadata(tmp_path):
    path = tmp_path / "fixtures" / "golden.json"
    record = {
        "model_id": "model",
        "model_revision": "revision",
        "prompt_token_ids": [1, 2],
        "output_token_ids": [3, 4],
        "runtime_versions": {"mlx": "test"},
    }

    reference_tokens.write_golden_fixture(path, record)

    assert json.loads(path.read_text()) == record
