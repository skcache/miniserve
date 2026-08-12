// MiniServe — Issue #23: Model Adapter Contract Tests
//
// Compile-only evidence for declared metadata and shape-facing types.
// Runtime forward/parity assertions must be added with the learner implementation.

#include <cstddef>
#include <type_traits>

#include "miniserve/model/adapter.hpp"

int main() {
    using miniserve::model::ModelMetadata;
    static_assert(std::is_same_v<decltype(ModelMetadata{}.vocabulary_size), std::size_t>);
    static_assert(std::is_same_v<decltype(ModelMetadata{}.maximum_context), std::size_t>);
    return 0;
}
