// MiniServe — Issue #27: Naive Concatenating KV Cache
//
// Role: compilation unit reserved for the copying correctness baseline.
// Responsibilities: append history, expose valid views, reset owned state.
// Does NOT own: preallocation, paged blocks, or scheduling.
// Key invariants: no cross-request aliasing; failed append preserves state.
// Evidence required: uncached/Python parity and reset/bounds tests.
// Implementation: TODO — Issue #27

#include "miniserve/cache/naive_cache.hpp"

namespace miniserve::cache {
// TODO — Issue #27: learner implementation belongs here.
}
