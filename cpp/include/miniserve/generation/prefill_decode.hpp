#pragma once

// MiniServe — Issue #25: Prefill and One-Token Decode Split
//
// Role:
// Declares the execution-phase boundary required by cache and latency work.
//
// Responsibilities:
// - process the prompt once during prefill
// - process one selected token during each decode step
// - carry explicit position and valid-length state
//
// Does NOT own:
// - cache layout
// - scheduling policy
// - batch admission
//
// Key invariants:
// - prefill consumes [batch, prompt_length]
// - decode consumes [batch, 1]
// - positions advance monotonically within a request
//
// Evidence required:
// - parity with the unsplit greedy path
// - call-shape and position tests
//
// Implementation: TODO — Issue #25

#include <cstddef>

namespace miniserve::generation {

struct ExecutionPosition {
    std::size_t prompt_length{};
    std::size_t decoded_length{};
};

class PrefillExecutor;
class DecodeExecutor;

}  // namespace miniserve::generation
