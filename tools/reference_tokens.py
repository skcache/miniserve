import argparse
import json
import platform
from importlib.metadata import version
from pathlib import Path

from mlx_lm import load, stream_generate

DEFAULT_MODEL_ID = "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
DEFAULT_MODEL_REVISION = "a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3"
DEFAULT_PROMPT = "What is the capital of France?"

REFERENCE_CASES = [
    {
        "name": "chat_short",
        "prompt": DEFAULT_PROMPT,
        "use_chat_template": True,
        "max_output_tokens": 8,
    },
    {
        "name": "plain_short",
        "prompt": "The capital of France is",
        "use_chat_template": False,
        "max_output_tokens": 8,
    },
    {
        "name": "chat_medium",
        "prompt": (
            "Summarize this in one sentence: During autoregressive inference, prefill "
            "processes the prompt in parallel. Decode then produces one token at a time "
            "while reusing keys and values from earlier positions."
        ),
        "use_chat_template": True,
        "max_output_tokens": 8,
    },
    {
        "name": "chat_eos",
        "prompt": "Reply with only the word OK.",
        "use_chat_template": True,
        "max_output_tokens": 16,
    },
]


def build_reference_prompt(tokenizer, prompt, use_chat_template):
    """Turn one prompt into token IDs using one explicit formatting path."""
    if use_chat_template:
        messages = [{"role": "user", "content": prompt}]
        return tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
        )

    return tokenizer.encode(prompt, add_special_tokens=False)


def collect_reference_greedy_tokens(model, tokenizer, prompt_token_ids, count):
    """Collect token IDs and the reason mlx-lm stopped generating."""
    if count < 1:
        raise ValueError("count must be at least 1")

    token_ids = []
    finish_reason = None

    for response in stream_generate(
        model,
        tokenizer,
        prompt_token_ids,
        max_tokens=count,
    ):
        token_ids.append(int(response.token))
        if response.finish_reason is not None:
            finish_reason = response.finish_reason

    return token_ids, finish_reason


def build_case_record(model, tokenizer, case):
    """Run one declared prompt case and return its parity evidence."""
    prompt_token_ids = build_reference_prompt(
        tokenizer,
        case["prompt"],
        case["use_chat_template"],
    )
    output_token_ids, finish_reason = collect_reference_greedy_tokens(
        model,
        tokenizer,
        prompt_token_ids,
        case["max_output_tokens"],
    )

    return {
        "name": case["name"],
        "prompt": case["prompt"],
        "prompt_format": "chat" if case["use_chat_template"] else "plain",
        "max_output_tokens": case["max_output_tokens"],
        "prompt_token_ids": prompt_token_ids,
        "output_token_ids": output_token_ids,
        "generated_output_tokens": len(output_token_ids),
        "finish_reason": finish_reason,
    }


def build_suite_record(model, tokenizer):
    """Capture the small fixed parity suite used by Python and C++."""
    return {
        "schema_version": 1,
        "model_id": DEFAULT_MODEL_ID,
        "model_revision": DEFAULT_MODEL_REVISION,
        "generation_strategy": "greedy_argmax",
        "eos_token_ids": sorted(int(token_id) for token_id in tokenizer.eos_token_ids),
        "runtime_versions": {
            "python": platform.python_version(),
            "mlx": version("mlx"),
            "mlx_lm": version("mlx-lm"),
        },
        "cases": [build_case_record(model, tokenizer, case) for case in REFERENCE_CASES],
    }


def write_golden_fixture(path, record):
    """Write a readable JSON fixture and create its parent folder if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n")


def main():
    """Load the pinned model and save one deterministic golden-token fixture."""
    parser = argparse.ArgumentParser(description="Capture mlx-lm oracle tokens")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("results/golden_tokens.json"))
    parser.add_argument("--plain", action="store_true")
    parser.add_argument(
        "--suite",
        action="store_true",
        help="capture the fixed plain, chat, and EOS-focused parity cases",
    )
    args = parser.parse_args()

    model, tokenizer = load(
        DEFAULT_MODEL_ID,
        revision=DEFAULT_MODEL_REVISION,
    )

    if args.suite:
        record = build_suite_record(model, tokenizer)
        generated_count = sum(case["generated_output_tokens"] for case in record["cases"])
    else:
        use_chat_template = not args.plain
        case = {
            "name": "command_line_prompt",
            "prompt": args.prompt,
            "use_chat_template": use_chat_template,
            "max_output_tokens": args.count,
        }
        record = {
            "schema_version": 1,
            "model_id": DEFAULT_MODEL_ID,
            "model_revision": DEFAULT_MODEL_REVISION,
            "generation_strategy": "greedy_argmax",
            "eos_token_ids": sorted(int(token_id) for token_id in tokenizer.eos_token_ids),
            "runtime_versions": {
                "python": platform.python_version(),
                "mlx": version("mlx"),
                "mlx_lm": version("mlx-lm"),
            },
            "cases": [build_case_record(model, tokenizer, case)],
        }
        generated_count = record["cases"][0]["generated_output_tokens"]

    write_golden_fixture(args.output, record)
    print(f"Wrote {generated_count} oracle tokens to {args.output}")


if __name__ == "__main__":
    main()
