"""Simple tests for the golden-token oracle helpers."""

import json
from types import SimpleNamespace

from tools import reference_tokens


class _Tokenizer:
    eos_token_ids = {2}

    def encode(self, prompt, add_special_tokens=False):
        assert add_special_tokens is False
        return [7, len(prompt)]

    def apply_chat_template(self, messages, **kwargs):
        assert len(messages) == 1
        assert messages[0]["role"] == "user"
        assert kwargs == {
            "add_generation_prompt": True,
            "tokenize": True,
        }
        return [1, 7, len(messages[0]["content"]), 2]


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
    responses = [
        SimpleNamespace(token=3, finish_reason=None),
        SimpleNamespace(token=4, finish_reason="length"),
    ]

    monkeypatch.setattr(reference_tokens, "stream_generate", lambda *args, **kwargs: responses)

    token_ids, finish_reason = reference_tokens.collect_reference_greedy_tokens(
        model=object(),
        tokenizer=object(),
        prompt_token_ids=[1, 2],
        count=2,
    )

    assert token_ids == [3, 4]
    assert finish_reason == "length"


def test_suite_records_model_identity_and_stop_metadata(monkeypatch):
    responses = [SimpleNamespace(token=2, finish_reason="stop")]
    monkeypatch.setattr(reference_tokens, "stream_generate", lambda *args, **kwargs: responses)

    record = reference_tokens.build_suite_record(object(), _Tokenizer())

    assert record["model_revision"] == "a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3"
    assert record["eos_token_ids"] == [2]
    assert {case["prompt_format"] for case in record["cases"]} == {"chat", "plain"}
    assert all(case["finish_reason"] == "stop" for case in record["cases"])


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
