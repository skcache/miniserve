"""Small tests for the Phase 0 benchmark calculations."""

from types import SimpleNamespace

from tools import reference_benchmark


def test_measure_generation_records_ttft_tpot_and_tokens(monkeypatch):
    responses = [
        SimpleNamespace(token=4, finish_reason=None, peak_memory=0.4),
        SimpleNamespace(token=5, finish_reason=None, peak_memory=0.5),
        SimpleNamespace(token=6, finish_reason="length", peak_memory=0.5),
    ]
    times = iter([0.0, 2.0, 2.5, 3.0])
    monkeypatch.setattr(reference_benchmark, "stream_generate", lambda *args, **kwargs: responses)

    sample = reference_benchmark.measure_generation(
        model=object(),
        tokenizer=object(),
        prompt_token_ids=[1, 2],
        max_output_tokens=3,
        clock=lambda: next(times),
    )

    assert sample["output_token_ids"] == [4, 5, 6]
    assert sample["finish_reason"] == "length"
    assert sample["ttft_seconds"] == 2.0
    assert sample["inter_token_seconds"] == [0.5, 0.5]
    assert sample["decode_tokens_per_second"] == 2.0
    assert sample["peak_memory_gb"] == 0.5


def test_summary_keeps_tail_latency_separate_from_median():
    samples = [
        {
            "ttft_seconds": 1.0,
            "inter_token_seconds": [0.1, 0.2],
            "total_seconds": 1.3,
            "decode_tokens_per_second": 6.0,
            "peak_memory_gb": 0.4,
        },
        {
            "ttft_seconds": 3.0,
            "inter_token_seconds": [0.3, 0.4],
            "total_seconds": 3.7,
            "decode_tokens_per_second": 3.0,
            "peak_memory_gb": 0.5,
        },
    ]

    summary = reference_benchmark.summarize_samples(samples)

    assert summary["ttft_p50_seconds"] == 2.0
    assert summary["ttft_p99_seconds"] > summary["ttft_p50_seconds"]
    assert summary["tpot_p50_seconds"] == 0.25
    assert summary["decode_tokens_per_second_median"] == 4.5
    assert summary["peak_memory_gb_max"] == 0.5
