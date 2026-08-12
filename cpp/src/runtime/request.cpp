// MiniServe — Issue #30: Request Lifecycle and Runtime Ownership
//
// Role: compilation unit reserved for request-local state and cleanup.
// Responsibilities: lifecycle, token state, limits, timestamps, terminal cause.
// Does NOT own: global scheduler policy, model weights, or HTTP transport.
// Key invariants: one mutation authority; one terminal cleanup path.
// Evidence required: transition, cancellation, failure, and cleanup tests.
// Implementation: TODO — Issue #30

#include "miniserve/runtime/request.hpp"

namespace miniserve::runtime {
// TODO — Issue #30: learner implementation belongs here.
}
