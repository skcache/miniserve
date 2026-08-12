#pragma once

// MiniServe — Issue #30: Request Lifecycle and Runtime Ownership
//
// Role:
// Defines request identity, lifecycle vocabulary, limits, and timestamps.
//
// Responsibilities:
// - represent normal and terminal lifecycle states
// - carry request-local generation limits and timing state
// - identify cleanup boundaries
//
// Does NOT own:
// - global scheduling policy
// - model weights
// - network transport
//
// Key invariants:
// - one authority mutates lifecycle state
// - every request reaches one terminal cleanup path
// - request-local state cannot cross request IDs
//
// Evidence required:
// - valid/invalid transition and cleanup tests
//
// Implementation: TODO — Issue #30

#include <chrono>
#include <cstddef>
#include <cstdint>

namespace miniserve::runtime {

using RequestId = std::uint64_t;

enum class RequestState {
    created,
    waiting,
    prefill,
    decoding,
    finished,
    cancelled,
    failed,
};

struct RequestLimits {
    std::size_t maximum_new_tokens{};
};

struct RequestTimestamps {
    std::chrono::steady_clock::time_point created;
    std::chrono::steady_clock::time_point admitted;
    std::chrono::steady_clock::time_point first_token;
    std::chrono::steady_clock::time_point terminal;
};

class Request;

}  // namespace miniserve::runtime
