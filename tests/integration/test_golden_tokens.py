"""Small contract tests for the Python golden-token oracle tooling."""

import json

import pytest

from tools.reference_tokens import build_reference_prompt, write_golden_fixture

pytestmark = pytest.mark.xfail(
    strict=True,
    reason="Golden-token oracle implementation remains open in issue #5",
)


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
    token_ids = build_reference_prompt(_Tokenizer(), "hello", use_chat_template=False)

    assert token_ids == [7, 5]


def test_chat_reference_prompt_uses_one_declared_template():
    token_ids = build_reference_prompt(_Tokenizer(), "hello", use_chat_template=True)

    assert token_ids == [1, 7, 5, 2]


def test_golden_fixture_preserves_reproducibility_metadata(tmp_path):
    path = tmp_path / "golden.json"
    record = {
        "model_id": "model",
        "model_revision": "revision",
        "prompt_token_ids": [1, 2],
        "output_token_ids": [3, 4],
        "runtime_versions": {"mlx": "test"},
    }

    write_golden_fixture(path, record)

    assert json.loads(path.read_text()) == record
