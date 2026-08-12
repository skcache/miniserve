// MiniServe — Issue #28: Preallocated Contiguous KV Cache
//
// Role: compilation unit reserved for fixed-capacity request K/V storage.
// Responsibilities: reserve, append, view, reset, and release.
// Does NOT own: admission, scheduling, or paged allocation.
// Key invariants: one allocation; bounded writes; initialized views only.
// Evidence required: naive/uncached/Python parity and reuse tests.
// Implementation: TODO — Issue #28

#include "miniserve/cache/contiguous_cache.hpp"

namespace miniserve::cache {
// TODO — Issue #28: learner implementation belongs here.
}
