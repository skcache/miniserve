// MiniServe — Issue #22: Python-to-C++ Parity Contract Tests
//
// Compile-only evidence that token fixtures use the runtime token type.
// Schema loading and exact token comparison remain learner implementation work.

#include <type_traits>
#include <vector>

#include "miniserve/runtime/parity.hpp"

int main() {
    using miniserve::TokenId;
    using miniserve::runtime::ParityFixture;

    static_assert(std::is_same_v<
                  decltype(ParityFixture{}.expected_output_token_ids),
                  std::vector<TokenId>>);
    return 0;
}
