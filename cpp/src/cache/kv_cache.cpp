// MiniServe — Issue #26: KV-Cache Interface and Ownership
//
// Role: compilation unit reserved for shared cache-contract behavior.
// Responsibilities: shape, capacity, valid length, bounds, and reset contract.
// Does NOT own: concrete storage, scheduling, or model weights.
// Key invariants: request isolation; valid length never exceeds capacity.
// Evidence required: shape, bounds, reset, and lifetime tests.
// Implementation: TODO — Issue #26

#include "miniserve/cache/kv_cache.hpp"

namespace miniserve::cache {
// TODO — Issue #26: choose the ownership interface before implementation.
}
