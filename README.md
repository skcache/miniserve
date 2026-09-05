# MiniServe

I started MiniServe because I have a genuine interest in language-model inference and want to understand every layer involved in turning model weights into generated tokens.

Right now, much of that path is hidden from me. A model-loading library reads the weights. A framework constructs the computation. A generation helper owns the decoding loop. The device runtime schedules the work. A serving framework handles requests and batching.

I want to open that path up and understand it from end to end.

MiniServe begins as a small inference engine for Apple Silicon. The first version uses Python and MLX to establish correct behavior, followed by a C++20 runtime where I will implement generation, KV caching, batching, scheduling, benchmarking, and a profile-selected Metal kernel.

The long-term goal is to own the complete inference path from model file to streamed token.

```text
model file
    ↓
tokenizer
    ↓
tensor runtime
    ↓
transformer
    ↓
prefill and decode
    ↓
KV memory manager
    ↓
request scheduler
    ↓
server
    ↓
streamed tokens
```

## Where MiniServe is right now

The Python side currently contains:

- reference attention and transformer operations
- a model and tokenizer adapter
- manual greedy generation
- deterministic token-oracle tooling
- small tests for shapes, token selection, causal behavior, and stopping

The native side currently contains:

- a C++20 Apple Silicon bootstrap that reports compiler, architecture, and build type
- optional MLX C++ linking against the same `mlx` package the Python oracle uses
- a tiny `mlx_link_smoke` check that constructs arrays; this is not model inference
- interfaces for model execution
- prefill and decode boundaries
- KV-cache interfaces
- request and scheduler types
- benchmark contracts
- a reserved boundary for Metal kernels

The C++ inference path is still under construction. Linking MLX C++ does not mean generation, caching, or scheduling works.

## The first complete runtime

The first major target is a small model generating text through code I can explain from beginning to end.

That means implementing:

1. model and tokenizer loading
2. a forward pass through MLX C++
3. manual greedy token selection
4. separate prefill and decode paths
5. a contiguous KV cache
6. request state and cancellation
7. static batching
8. iteration-level batching
9. reproducible latency measurements
10. one custom Metal kernel selected from profiling

The model is small enough to run safely on my M2 Pro. The difficult part of this project is the runtime, memory, and scheduling behavior, not fitting the largest possible model into memory.

The implementation work is tracked in the [GitHub issue backlog](https://github.com/skcache/miniserve/issues).

## Correctness

Every optimization begins with a slower implementation that is easier to inspect.

The Python runtime records a pinned model revision, prompt token IDs, generated token IDs, and runtime versions. The C++ runtime must reproduce the same greedy token sequence.

Small tests cover individual properties:

```text
causal attention cannot read future tokens
final-position logits select the next token
one decode iteration appends one token
the EOS token appears once and stops generation
prefill and decode preserve the expected tensor shapes
cached and uncached generation produce the same tokens
```

These tests are small. I want failures to tell me which inference rule I misunderstood.

## Experiments

MiniServe is organized around comparisons.

### Full-sequence generation and cached generation

The uncached decoder repeatedly processes the growing sequence:

```text
[prompt]
[prompt, token 1]
[prompt, token 1, token 2]
[prompt, token 1, token 2, token 3]
```

The cached decoder processes the prompt once and stores attention keys and values for later decode steps.

I will compare token parity, time to first token, time per output token, total latency, and memory use.

### Growing and preallocated KV caches

The first cache grows by concatenating tensors. The second reserves capacity and writes into known positions.

This experiment is meant to expose allocation, copying, capacity, tensor layout, and ownership before moving to block-based memory.

### Static and iteration-level batching

Static batching keeps a group of requests together until generation finishes.

Iteration-level batching rebuilds the active batch between decoding steps. Finished requests can leave and waiting requests can enter.

This part of MiniServe will measure throughput, queueing delay, batch utilization, P50 latency, and P99 latency.

### Metal

I will profile the runtime before choosing a Metal kernel.

The selected operation will have three implementations:

```text
readable reference
MLX C++
Metal
```

All three must produce matching results. The report will include raw timings and unsuccessful attempts, including cases where MLX is already faster.

## Measurements

Each benchmark records:

- hardware and operating-system version
- model name and exact revision
- weight precision
- prompt and output lengths
- request arrival pattern
- cache configuration
- scheduler policy
- warmup procedure
- synchronization points
- raw samples
- summary statistics

The main metrics are:

| Metric | What it captures |
|---|---|
| TTFT | Time from admission to the first token |
| TPOT | Time per output token after prefill |
| End-to-end latency | Total request lifetime |
| Throughput | Output tokens produced per second |
| P50 and P99 | Typical and tail latency |
| KV memory | Cache memory used as context grows |
| Batch utilization | Active scheduler slots over time |

### Phase 0 reference measurements

The first measured baseline uses the pinned Qwen2.5 0.5B 4-bit model through `mlx-lm` on an M2 Pro with 16 GB of unified memory. The formatted chat prompt contains 36 tokens. Generation requests at most 16 output tokens and stops naturally on EOS after 8. Each result below uses one warmup followed by three measured runs.

The battery run was captured at commit `8f9528d`. The plugged-in run used the same benchmark code and workload at commit `f68055e`. Both ran on macOS 26.5.2 with Python 3.12.0, MLX 0.32.0, and mlx-lm 0.31.3.

| Metric | Battery | Plugged in | Change |
|---|---:|---:|---:|
| Model load | 478.89 ms | 650.76 ms | +35.89% |
| TTFT P50 | 104.97 ms | 100.20 ms | -4.54% |
| TTFT P99 | 107.20 ms | 103.24 ms | -3.69% |
| TPOT P50 | 3.28 ms | 3.21 ms | -2.06% |
| TPOT P99 | 3.79 ms | 4.36 ms | +14.91% |
| Total latency P50 | 128.40 ms | 123.98 ms | -3.45% |
| Median decode throughput | 300.92 tokens/s | 302.14 tokens/s | +0.41% |
| Reported peak MLX memory | 0.338 GB | 0.338 GB | 0.00% |

All six measured runs produced the same eight token IDs and ended on EOS. Lower is better for latency rows. Higher is better for throughput. The benchmark records raw per-token timings under ignored `results/`.

The plugged-in run had modestly lower median latency, while decode throughput was effectively unchanged and TPOT P99 was worse. Three runs per condition cannot isolate power state from thermal state, memory pressure, or background activity, so this is a local smoke comparison rather than evidence that AC power caused a speedup. The measurement includes the high-level Python and `mlx-lm` path. It does not measure the future MiniServe C++ runtime.

The plugged-in measurement was collected while the laptop was also running normal desktop applications, including a browser and the development environment. That makes the 35.89% increase in model-load time especially vulnerable to host CPU, memory, and filesystem contention. These numbers are retained as preliminary evidence, but both power conditions need to be rerun in a quiet session with only the benchmark and its development terminal open before making a power-state comparison.

## Building the Python reference

MiniServe uses native ARM Python 3.12 and `uv`.

```bash
uv sync
uv run pytest
uv run python tools/hardware_report.py
```

Capture reference tokens:

```bash
make oracle
```

Run the small reference benchmark:

```bash
make benchmark
```

Run the complete Phase 0 evidence path:

```bash
make phase0
```

The reviewed Python/C++ parity contract lives at `tests/fixtures/golden_tokens.json`. It freezes plain, chat, and EOS-focused cases against the full model revision. Machine-specific reports and regenerated evidence are written beneath ignored `results/`.

The benchmark preserves raw per-token timings and reports TTFT, TPOT, total latency, decode throughput, and peak MLX memory. Each record includes the model revision, current Git commit, hardware report, power state, runtime versions, and timing method. These measurements establish a local baseline. They are not cross-hardware performance claims.

## Building the native scaffold

The default native build does not link MLX. It proves C++20, CMake, and process identity:

```bash
make cpp-test
./cpp/build/miniserve_cpp
```

MLX C++ is discovered at configure time. The Python `mlx` package already ships `mlx/array.h`, `libmlx`, and `MLXConfig.cmake`. From this repository:

```bash
make cpp-test-mlx
./cpp/build-mlx/miniserve_cpp
```

`make cpp-test-mlx` asks the project interpreter for `python -m mlx --cmake-dir` and passes that directory as `MLX_CPP_ROOT`. You can also let CMake probe `../.venv/bin/python`, or point at a from-source install:

```bash
cmake -S cpp -B cpp/build-mlx \
  -DCMAKE_BUILD_TYPE=Debug \
  -DMINISERVE_ENABLE_MLX=ON \
  -DMLX_CPP_ROOT=/path/to/mlx/prefix
```

Do not commit a machine-local prefix. On Apple, CMake pins `arm64` unless you override `CMAKE_OSX_ARCHITECTURES`, because the Python `mlx` wheel is Apple Silicon. Successful configuration and a passing `mlx_link_smoke` prove headers and `libmlx` were found. They do not mean native model inference works.

## Repository map

```text
src/minsrv/                 Python reference implementation
tests/                      Small Python correctness tests
tools/                      Oracle, hardware, and execution experiments

cpp/include/miniserve/      Native runtime interfaces
cpp/src/                    C++ implementation
cpp/tests/                  Native correctness tests
cpp/kernels/                Metal kernels

results/                    Ignored local measurements
```

Private study notes, architecture reasoning, and local measurements stay out of the public repository.

## Longer-term direction

The C++ runtime is the beginning of MiniServe.

Over time, I want to replace more of the borrowed stack with code built inside this repository: model-file parsing, tokenization, tensor storage, Metal execution, quantization, paged KV allocation, prefix reuse, scheduling, serving, and tools for inspecting a live inference request.

The final project should make it possible to follow one token from input text, through every transformer layer and cache allocation, until it is streamed back to the client.
