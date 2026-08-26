"""Measure a small reproducible mlx-lm reference generation baseline."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
from importlib.metadata import version
from math import ceil, floor
from pathlib import Path
from statistics import median

from mlx_lm import load, stream_generate

from tools.reference_tokens import (
    DEFAULT_MODEL_ID,
    DEFAULT_MODEL_REVISION,
    DEFAULT_PROMPT,
    build_reference_prompt,
)

DEFAULT_OUTPUT = Path("results/reference_benchmark.json")
HARDWARE_REPORT = Path("results/hardware.json")


def percentile(values, fraction):
    """Return a linearly interpolated percentile from a non-empty list."""
    if not values:
        return None

    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = floor(position)
    upper = ceil(position)

    if lower == upper:
        return ordered[lower]

    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def measure_generation(model, tokenizer, prompt_token_ids, max_output_tokens, clock=None):
    """Measure one generation and retain raw token-level timing evidence."""
    clock = clock or time.perf_counter
    started_at = clock()
    token_times = []
    output_token_ids = []
    finish_reason = None
    peak_memory_gb = 0.0

    for response in stream_generate(
        model,
        tokenizer,
        prompt_token_ids,
        max_tokens=max_output_tokens,
    ):
        token_times.append(clock())
        output_token_ids.append(int(response.token))
        finish_reason = response.finish_reason or finish_reason
        peak_memory_gb = max(peak_memory_gb, float(response.peak_memory))

    ttft_seconds = token_times[0] - started_at
    total_seconds = token_times[-1] - started_at
    inter_token_seconds = [
        current - previous for previous, current in zip(token_times, token_times[1:])
    ]
    decode_seconds = sum(inter_token_seconds)
    decode_tokens_per_second = (
        len(inter_token_seconds) / decode_seconds if decode_seconds > 0 else None
    )

    return {
        "prompt_tokens": len(prompt_token_ids),
        "output_token_ids": output_token_ids,
        "output_tokens": len(output_token_ids),
        "finish_reason": finish_reason,
        "ttft_seconds": ttft_seconds,
        "inter_token_seconds": inter_token_seconds,
        "total_seconds": total_seconds,
        "decode_tokens_per_second": decode_tokens_per_second,
        "peak_memory_gb": peak_memory_gb,
    }


def summarize_samples(samples):
    """Summarize repeated runs while preserving the raw samples separately."""
    ttft = [sample["ttft_seconds"] for sample in samples]
    inter_token = [value for sample in samples for value in sample["inter_token_seconds"]]
    total = [sample["total_seconds"] for sample in samples]
    throughput = [
        sample["decode_tokens_per_second"]
        for sample in samples
        if sample["decode_tokens_per_second"] is not None
    ]

    return {
        "measured_runs": len(samples),
        "ttft_p50_seconds": percentile(ttft, 0.50),
        "ttft_p99_seconds": percentile(ttft, 0.99),
        "tpot_p50_seconds": percentile(inter_token, 0.50),
        "tpot_p99_seconds": percentile(inter_token, 0.99),
        "total_p50_seconds": percentile(total, 0.50),
        "decode_tokens_per_second_median": median(throughput) if throughput else None,
        "peak_memory_gb_max": max(sample["peak_memory_gb"] for sample in samples),
    }


def git_commit():
    """Return the current commit without making Git metadata mandatory."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def load_hardware_report():
    """Include the local hardware report when it has already been generated."""
    if not HARDWARE_REPORT.exists():
        return None
    return json.loads(HARDWARE_REPORT.read_text())


def main():
    parser = argparse.ArgumentParser(description="Benchmark the pinned mlx-lm reference path")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--max-output-tokens", type=int, default=16)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--plain", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.max_output_tokens < 2:
        parser.error("--max-output-tokens must be at least 2 for TPOT measurement")
    if args.warmups < 0:
        parser.error("--warmups cannot be negative")
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")

    load_started_at = time.perf_counter()
    model, tokenizer = load(DEFAULT_MODEL_ID, revision=DEFAULT_MODEL_REVISION)
    model_load_seconds = time.perf_counter() - load_started_at

    use_chat_template = not args.plain
    prompt_token_ids = build_reference_prompt(tokenizer, args.prompt, use_chat_template)

    for _ in range(args.warmups):
        measure_generation(
            model,
            tokenizer,
            prompt_token_ids,
            args.max_output_tokens,
        )

    samples = []
    for run_number in range(1, args.repeats + 1):
        sample = measure_generation(
            model,
            tokenizer,
            prompt_token_ids,
            args.max_output_tokens,
        )
        sample["run"] = run_number
        samples.append(sample)

    record = {
        "schema_version": 1,
        "benchmark": "mlx_lm_reference_greedy_generation",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": git_commit(),
        "model_id": DEFAULT_MODEL_ID,
        "model_revision": DEFAULT_MODEL_REVISION,
        "prompt": args.prompt,
        "prompt_format": "chat" if use_chat_template else "plain",
        "max_output_tokens": args.max_output_tokens,
        "warmup_runs": args.warmups,
        "model_load_seconds": model_load_seconds,
        "runtime_versions": {
            "python": platform.python_version(),
            "mlx": version("mlx"),
            "mlx_lm": version("mlx-lm"),
        },
        "timing_method": {
            "clock": "time.perf_counter",
            "ttft": "generation start through the first materialized token",
            "tpot": "wall time between consecutive materialized tokens",
            "synchronization": (
                "mlx-lm materializes each sampled token before stream_generate yields it; "
                "the benchmark timestamps immediately after each yield"
            ),
        },
        "hardware": load_hardware_report(),
        "summary": summarize_samples(samples),
        "samples": samples,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2) + "\n")

    summary = record["summary"]
    print(f"TTFT P50: {summary['ttft_p50_seconds'] * 1_000:.2f} ms")
    print(f"TPOT P50: {summary['tpot_p50_seconds'] * 1_000:.2f} ms")
    print(f"Decode throughput: {summary['decode_tokens_per_second_median']:.2f} tok/s")
    print(f"Wrote benchmark evidence to {args.output}")


if __name__ == "__main__":
    main()
