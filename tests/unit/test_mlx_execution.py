"""Small tests for the MLX execution lab."""

import mlx.core as mx
import torch

from tools.mlx_execution_lab import (
    build_equivalent_mlx_mlp,
    build_equivalent_torch_mlp,
    run_on_stream,
    time_with_evaluation,
)


def _shared_values():
    inputs = [[[1.0, 2.0], [3.0, 4.0]]]
    up_weight = [[0.5, -0.5, 1.0], [1.0, 0.5, -1.0]]
    down_weight = [[1.0, 0.0], [0.0, 1.0], [0.5, -0.5]]
    return inputs, up_weight, down_weight


def test_torch_and_mlx_mlp_outputs_match_with_shared_parameters():
    inputs, up_weight, down_weight = _shared_values()

    torch_output = build_equivalent_torch_mlp(
        {
            "up_weight": torch.tensor(up_weight, dtype=torch.float32),
            "down_weight": torch.tensor(down_weight, dtype=torch.float32),
        },
        torch.tensor(inputs, dtype=torch.float32),
    )
    mlx_output = build_equivalent_mlx_mlp(
        {
            "up_weight": mx.array(up_weight, dtype=mx.float32),
            "down_weight": mx.array(down_weight, dtype=mx.float32),
        },
        mx.array(inputs, dtype=mx.float32),
    )
    mx.eval(mlx_output)

    assert torch.allclose(
        torch_output,
        torch.tensor(mlx_output.tolist()),
        atol=1e-5,
        rtol=1e-5,
    )


def test_cpu_and_gpu_stream_outputs_match():
    inputs = mx.array([1.0, 2.0, 3.0])

    def double(values):
        return values * 2

    cpu_output = run_on_stream(double, inputs, mx.default_stream(mx.cpu))
    gpu_output = run_on_stream(double, inputs, mx.default_stream(mx.gpu))
    mx.eval(cpu_output, gpu_output)

    assert cpu_output.tolist() == gpu_output.tolist()


def test_timing_helper_returns_one_sample_per_repeat():
    samples = time_with_evaluation(
        lambda values: values + 1,
        mx.array([1.0, 2.0]),
        warmups=1,
        repeats=3,
    )

    assert len(samples) == 3


def test_different_shapes_stay_separate_benchmark_inputs():
    small = mx.ones((2, 2))
    large = mx.ones((4, 4))

    assert small.shape != large.shape
