// MiniServe — Issue #24: Explicit Greedy Autoregressive Decode
//
// Role: compilation unit reserved for MiniServe-owned token generation.
// Responsibilities: final-position argmax, append, stop, and token trace.
// Does NOT own: model weights, KV layout, batching, or scheduling.
// Key invariants: deterministic one-token decisions; explicit EOS semantics.
// Evidence required: exact Python-reference token parity.
// Implementation: TODO — Issue #24

#include "miniserve/generation/generation.hpp"

namespace miniserve::generation {
// TODO — Issue #24: learner implementation belongs here.
}
