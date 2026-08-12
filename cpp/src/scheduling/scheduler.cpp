// MiniServe — Issue #32: Scheduler Iteration Loop
//
// Role: compilation unit reserved for the single execution owner.
// Responsibilities: admit, dispatch one phase, observe terminal state, cleanup.
// Does NOT own: batch tensor layout, persistence, priority, or preemption.
// Key invariants: one request failure cannot corrupt another request.
// Evidence required: deterministic fake-executor ordering/isolation tests.
// Implementation: TODO — Issue #32

#include "miniserve/scheduling/scheduler.hpp"

namespace miniserve::scheduling {
// TODO — Issue #32: learner implementation belongs here.
}
