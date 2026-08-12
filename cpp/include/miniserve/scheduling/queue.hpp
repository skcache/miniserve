#pragma once

// MiniServe — Issue #31: Waiting Queue and Active Request Ownership
//
// Role:
// Names bounded waiting and active-request ownership boundaries.
//
// Responsibilities:
// - enforce configured capacities
// - transfer one request between ownership domains
// - make terminal removal idempotent
//
// Does NOT own:
// - scheduler policy
// - model execution
// - durable persistence
//
// Key invariants:
// - a request cannot exist in both collections
// - active count never exceeds capacity
// - terminal requests are not retained
//
// Evidence required:
// - capacity, transfer, duplicate, and cleanup tests
//
// Implementation: TODO — Issue #31

#include <cstddef>

namespace miniserve::scheduling {

struct RuntimeCapacity {
    std::size_t maximum_waiting{};
    std::size_t maximum_active{};
};

class WaitingQueue;
class ActiveRequestSet;

}  // namespace miniserve::scheduling
