// MiniServe — Issues #24 and #25: Generation Contract Tests
//
// Compile-only evidence for deterministic limits and per-step state.
// Token-selection, EOS, prefill, and decode parity tests remain learner work.

#include <cstddef>
#include <type_traits>

#include "miniserve/generation/generation.hpp"
#include "miniserve/generation/prefill_decode.hpp"

int main() {
    using miniserve::generation::ExecutionPosition;
    using miniserve::generation::GenerationConfig;
    using miniserve::generation::GenerationStep;

    static_assert(std::is_same_v<decltype(GenerationConfig{}.maximum_new_tokens), std::size_t>);
    static_assert(std::is_same_v<decltype(GenerationStep{}.sequence_length), std::size_t>);
    static_assert(std::is_same_v<decltype(ExecutionPosition{}.decoded_length), std::size_t>);
    return 0;
}
