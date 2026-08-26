"""Checks for the small committed Python/C++ parity contract."""

import json
from pathlib import Path

FIXTURE = Path(__file__).parents[1] / "fixtures" / "golden_tokens.json"


def test_golden_fixture_has_plain_chat_and_eos_evidence():
    record = json.loads(FIXTURE.read_text())
    cases = {case["name"]: case for case in record["cases"]}

    assert record["schema_version"] == 1
    assert len(record["model_revision"]) == 40
    assert {case["prompt_format"] for case in cases.values()} == {"plain", "chat"}
    assert cases["chat_eos"]["finish_reason"] == "stop"
    assert cases["chat_eos"]["output_token_ids"][-1] in record["eos_token_ids"]
    assert cases["plain_short"]["finish_reason"] == "length"
    assert len(cases["plain_short"]["output_token_ids"]) == 8


def test_golden_fixture_counts_match_the_recorded_tokens():
    record = json.loads(FIXTURE.read_text())

    for case in record["cases"]:
        assert case["generated_output_tokens"] == len(case["output_token_ids"])
        assert all(isinstance(token_id, int) for token_id in case["prompt_token_ids"])
        assert all(isinstance(token_id, int) for token_id in case["output_token_ids"])
