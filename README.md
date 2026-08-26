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

- a C++20 build
- interfaces for model execution
- prefill and decode boundaries
- KV-cache interfaces
- request and scheduler types
- benchmark contracts
- a reserved boundary for Metal kernels

The C++ inference path is still under construction. A source file existing does not mean the subsystem works.

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

```bash
cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Debug
cmake --build cpp/build
ctest --test-dir cpp/build --output-on-failure
./cpp/build/miniserve_cpp
```

To test the MLX C++ discovery boundary:

```bash
cmake -S cpp -B cpp/build-mlx \
  -DMINISERVE_ENABLE_MLX=ON \
  -DMLX_CPP_ROOT=/path/to/mlx/prefix
```

Successful configuration proves that the headers and libraries were discovered. Native model inference is not complete yet.

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
