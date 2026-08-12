#pragma once

// MiniServe — Issue #36: Repeatable Benchmark Infrastructure
//
// Role:
// Defines measurement metadata and raw-sample records.
//
// Responsibilities:
// - identify hardware, runtime, model, and workload
// - distinguish cold/warm and synchronized samples
// - preserve raw values used by summaries
//
// Does NOT own:
// - runtime optimization choices
// - benchmark thresholds
// - remote telemetry
//
// Key invariants:
// - summary values are reproducible from raw samples
// - incomparable metadata is not silently aggregated
// - machine-specific results remain uncommitted
//
// Evidence required:
// - schema and synthetic summary tests
//
// Implementation: TODO — Issue #36

#include <cstddef>
#include <string>
#include <vector>

#include "miniserve/runtime/types.hpp"

namespace miniserve::benchmarks {

struct BenchmarkCase {
    std::string name;
    std::string hardware;
    std::string mlx_version;
    ModelIdentity model;
    std::size_t prompt_length{};
    std::size_t generated_tokens{};
    std::size_t concurrency{};
    bool cold{};
};

struct TimingSample {
    double ttft_ms{};
    std::vector<double> inter_token_ms;
    double total_tokens_per_second{};
    std::size_t kv_bytes{};
    std::size_t peak_memory_bytes{};
};

}  // namespace miniserve::benchmarks
