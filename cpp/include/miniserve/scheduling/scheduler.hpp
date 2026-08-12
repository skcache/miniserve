#pragma once

// MiniServe — Issue #32: Scheduler Iteration Loop
//
// Role:
// Declares a single iteration owner for admission, execution, and cleanup.
//
// Responsibilities:
// - admit work at iteration boundaries
// - dispatch prefill or one decode step
// - remove terminal requests and release resources
//
// Does NOT own:
// - tensor batch layout
// - persistent queues
// - priority or preemption policy
//
// Key invariants:
// - one component mutates active execution state
// - one request failure cannot corrupt another
// - terminal resources are released exactly once
//
// Evidence required:
// - deterministic fake-executor ordering and isolation tests
//
// Implementation: TODO — Issue #32

#include <cstddef>

namespace miniserve::scheduling {

struct SchedulerSnapshot {
    std::size_t waiting_count{};
    std::size_t active_count{};
    std::size_t completed_count{};
    std::size_t iteration{};
};

class Scheduler;

}  // namespace miniserve::scheduling
