// MiniServe — Issues #30–#34: Request and Scheduler Contract Tests
//
// Compile-only evidence for lifecycle and capacity vocabulary.
// Transition, queue, tick, batching, and slot-reuse tests remain learner work.

#include <cstddef>
#include <type_traits>

#include "miniserve/runtime/request.hpp"
#include "miniserve/scheduling/queue.hpp"
#include "miniserve/scheduling/scheduler.hpp"

int main() {
    using miniserve::runtime::RequestState;
    using miniserve::scheduling::RuntimeCapacity;
    using miniserve::scheduling::SchedulerSnapshot;

    static_assert(RequestState::created != RequestState::finished);
    static_assert(RequestState::cancelled != RequestState::failed);
    static_assert(std::is_same_v<decltype(RuntimeCapacity{}.maximum_active), std::size_t>);
    static_assert(std::is_same_v<decltype(SchedulerSnapshot{}.iteration), std::size_t>);
    return 0;
}
