// MiniServe — Issue #25: Prefill and One-Token Decode Split
//
// Role: compilation unit reserved for phase-specific execution.
// Responsibilities: prompt prefill, one-token decode, and position handoff.
// Does NOT own: cache layout, batch admission, or scheduler policy.
// Key invariants: prefill consumes prompt once; decode consumes [B,1].
// Evidence required: unsplit-path parity and call-shape tests.
// Implementation: TODO — Issue #25

#include "miniserve/generation/prefill_decode.hpp"

namespace miniserve::generation {
// TODO — Issue #25: learner implementation belongs here.
}
