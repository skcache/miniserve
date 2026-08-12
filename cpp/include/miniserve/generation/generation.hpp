#pragma once

// MiniServe — Issue #24: Explicit Greedy Autoregressive Decode
//
// Role:
// Declares deterministic token-by-token generation owned by MiniServe.
//
// Responsibilities:
// - select the final-position greedy token
// - enforce EOS and maximum-output limits
// - return an inspectable token trace
//
// Does NOT own:
// - model weights
// - KV storage
// - request scheduling
//
// Key invariants:
// - exactly one token decision per decode step
// - EOS is represented consistently in the trace
// - no framework generation helper is called
//
// Evidence required:
// - exact parity with the Python reference fixture
// - deterministic stop-condition tests
//
// Implementation: TODO — Issue #24

#include <cstddef>
#include <vector>

#include "miniserve/runtime/types.hpp"

namespace miniserve::model {
class ModelAdapter;
}

namespace miniserve::generation {

struct GenerationConfig {
    std::size_t maximum_new_tokens{};
    std::vector<TokenId> eos_token_ids;
};

struct GenerationStep {
    std::size_t index{};
    TokenId token_id{};
    std::size_t sequence_length{};
    bool is_eos{};
};

struct GenerationResult {
    std::vector<TokenId> token_ids;
    std::vector<GenerationStep> steps;
};

[[nodiscard]] GenerationResult generate_greedy(
    model::ModelAdapter& adapter,
    const std::vector<TokenId>& prompt_token_ids,
    const GenerationConfig& config);

}  // namespace miniserve::generation
