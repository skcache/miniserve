# MiniServe

MiniServe is a focused C++20 language-model inference runtime project for Apple Silicon. The native runtime will use the MLX C++ API and finish with one custom Metal optimization selected from profiling evidence.

The existing Python implementation is retained as the correctness oracle. It defines the expected prompt tokens, greedy output tokens, tensor shapes, and small reference behavior used to verify the native path.

## Current state

The repository contains:

- learner-authored Python reference components;
- small Python correctness tests and oracle tooling;
- a compile-only C++20 project scaffold;
- interface contracts linked to the [C++ V1 issue backlog](https://github.com/skcache/miniserve/issues);
- no implemented native inference, KV-cache, batching, scheduler, or Metal algorithm yet.

Every unimplemented native subsystem is identified by its real GitHub issue number. Empty source files and compile-time contract tests establish boundaries without solving the implementation.

## 30-day C++ V1

The required path is:

1. bootstrap MLX C++ and prove Python/C++ token parity;
2. implement explicit greedy generation with separate prefill and decode;
3. compare naive concatenating and preallocated contiguous KV caches;
4. add request lifecycles, static batching, and fixed-slot continuous batching;
5. measure deterministic synthetic workloads;
6. profile the runtime, choose one operation, and compare readable, MLX C++, and Metal implementations;
7. publish reproducible evidence, including negative optimization results.

The first native issue is [#21 — Bootstrap the C++20 and MLX C++ runtime](https://github.com/skcache/miniserve/issues/21). The Python reference gate in [#5](https://github.com/skcache/miniserve/issues/5) remains ahead of it on the critical path.

## Scope boundaries

Required for V1:

- Python correctness oracle;
- C++20 and MLX C++;
- manual greedy autoregressive decode;
- explicit prefill/decode phases;
- naive and preallocated contiguous KV caches;
- request lifecycle and scheduler;
- static and fixed-slot continuous batching;
- CLI synthetic load and repeatable benchmarks;
- one profile-selected Metal kernel;
- technical report.

Not part of V1:

- quantization work;
- Mixture of Experts;
- prefix caching or paged KV allocation;
- speculative decoding;
- HTTP/OpenAI-compatible serving;
- Triton, CUDA, distributed, multi-GPU, or multi-node inference.

## Python reference environment

Python uses `uv` with native ARM Python 3.12:

```bash
uv sync
uv run pytest
uv run python tools/hardware_report.py
```

The hardware command writes machine-specific output under ignored `results/`.

## C++ scaffold

The compile-only scaffold has no external test framework and builds without MLX by default:

```bash
cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Debug
cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
./cpp/build/miniserve_cpp
```

To exercise the MLX C++ configuration boundary, point CMake at a locally built MLX prefix:

```bash
cmake -S cpp -B cpp/build-mlx \
  -DMINISERVE_ENABLE_MLX=ON \
  -DMLX_CPP_ROOT=/path/to/mlx/prefix
```

That option verifies header/library discovery only. It does not imply that native model inference is implemented.

## Repository layout

```text
src/minsrv/                 Python reference implementation
tests/                      Python correctness and parity tests
tools/                      Oracle and hardware utilities
cpp/include/miniserve/      Native subsystem contracts
cpp/src/                    Learner-owned implementation surfaces
cpp/tests/                  Compile-time interface test scaffolds
cpp/kernels/                Profile-gated Metal boundary
results/                    Ignored local measurements
```

Private notes, architecture reasoning, and learning materials remain ignored and are not part of the public repository.
