#pragma once

// MiniServe — Issue #28: Preallocated Contiguous KV Cache
//
// Role:
// Names fixed-capacity request-local K/V storage.
//
// Responsibilities:
// - reserve configured capacity once
// - append into the next valid region
// - expose initialized cache views
// - reset and release owned storage
//
// Does NOT own:
// - admission capacity
// - scheduling policy
// - paged allocation
//
// Key invariants:
// - valid length is distinct from allocated capacity
// - append never concatenates full history
// - no write crosses the capacity boundary
//
// Evidence required:
// - naive/uncached/Python parity
// - capacity, reset, reuse, and isolation tests
//
// Implementation: TODO — Issue #28

namespace miniserve::cache {

class ContiguousKvCache;

}  // namespace miniserve::cache
