import argparse
import json
import platform
from importlib.metadata import version
from pathlib import Path

from mlx_lm import load, stream_generate

DEFAULT_MODEL_ID = "mlx-community/Qwen2.5-0.5B-Instruct-4bit"
DEFAULT_MODEL_REVISION = "a5339a4"
DEFAULT_PROMPT = "What is the capital of France?"


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
    """Collect exactly the token IDs emitted by mlx-lm's greedy oracle path."""
    if count < 1:
        raise ValueError("count must be at least 1")

    token_ids = []

    for response in stream_generate(
        model,
        tokenizer,
        prompt_token_ids,
        max_tokens=count,
    ):
        token_ids.append(int(response.token))

    return token_ids


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
    args = parser.parse_args()

    model, tokenizer = load(
        DEFAULT_MODEL_ID,
        revision=DEFAULT_MODEL_REVISION,
    )

    use_chat_template = not args.plain
    prompt_token_ids = build_reference_prompt(tokenizer, args.prompt, use_chat_template)
    output_token_ids = collect_reference_greedy_tokens(model, tokenizer, prompt_token_ids, args.count)

    record = {
        "model_id": DEFAULT_MODEL_ID,
        "model_revision": DEFAULT_MODEL_REVISION,
        "prompt": args.prompt,
        "use_chat_template": use_chat_template,
        "prompt_token_ids": prompt_token_ids,
        "output_token_ids": output_token_ids,
        "runtime_versions": {
            "python": platform.python_version(),
            "mlx": version("mlx"),
            "mlx_lm": version("mlx-lm"),
        },
    }

    write_golden_fixture(args.output, record)
    print(f"Wrote {len(output_token_ids)} oracle tokens to {args.output}")


if __name__ == "__main__":
    main()
