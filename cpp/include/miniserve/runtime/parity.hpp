#pragma once

// MiniServe — Issue #22: Python-to-C++ Parity Contract
//
// Role:
// Defines fixture metadata consumed by both correctness paths.
//
// Responsibilities:
// - identify model, tokenizer, prompt, and runtime
// - carry expected prompt/output token IDs
// - report structural or value mismatches
//
// Does NOT own:
// - model execution
// - fixture generation inside the C++ runtime
// - benchmark results
//
// Key invariants:
// - model/revision and prompt formatting are explicit
// - exact-token and tolerance comparisons are not conflated
// - missing metadata is a validation failure
//
// Evidence required:
// - schema validation and mismatch-reporting tests
//
// Implementation: TODO — Issue #22

#include <cstddef>
#include <string>
#include <vector>

#include "miniserve/runtime/types.hpp"

namespace miniserve::runtime {

struct ParityFixture {
    ModelIdentity model;
    std::string tokenizer_mode;
    std::string prompt;
    std::vector<TokenId> prompt_token_ids;
    std::size_t requested_output_tokens{};
    std::vector<TokenId> expected_output_token_ids;
    std::string oracle_runtime;
};

struct ParityResult {
    bool matches{};
    std::string mismatch;
};

[[nodiscard]] ParityResult compare_token_trace(
    const ParityFixture& fixture,
    const std::vector<TokenId>& actual_token_ids);

}  // namespace miniserve::runtime
