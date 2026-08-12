#pragma once

// MiniServe — Issue #27: Naive Concatenating KV Cache
//
// Role:
// Names the request-local correctness baseline for cache accumulation.
//
// Responsibilities:
// - accumulate per-layer K/V history
// - make append copying measurable
// - expose valid history to decode
//
// Does NOT own:
// - scheduling
// - preallocated storage
// - paged allocation
//
// Key invariants:
// - one cache instance cannot serve unrelated requests
// - reset removes all valid history
// - append failure leaves previous state valid
//
// Evidence required:
// - uncached/Python parity
// - empty, bounds, reset, and multi-layer tests
//
// Implementation: TODO — Issue #27

namespace miniserve::cache {

class NaiveKvCache;

}  // namespace miniserve::cache
