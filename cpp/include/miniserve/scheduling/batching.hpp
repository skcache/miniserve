#pragma once

// MiniServe — Issues #33 and #34: Static and Fixed-Slot Continuous Batching
//
// Role:
// Defines batch shape and request/row mapping vocabulary.
//
// Responsibilities:
// - preserve request identity across batch rows
// - represent unequal prompt lengths and independent stop state
// - make fixed active-slot capacity explicit
//
// Does NOT own:
// - request persistence
// - paged KV allocation
// - preemption or priority policy
//
// Key invariants:
// - padding cannot alter another request's positions
// - slot reuse clears all request-local state
// - row-to-request mapping remains stable for an iteration
//
// Evidence required:
// - isolated-vs-batched parity
// - slot refill, cancellation, and state-isolation tests
//
// Implementation: TODO — Issues #33 and #34

#include <cstddef>

namespace miniserve::scheduling {

struct BatchShape {
    std::size_t batch_size{};
    std::size_t padded_sequence_length{};
};

class StaticBatch;
class ContinuousBatch;

}  // namespace miniserve::scheduling
