#pragma once

// MiniServe — Issue #23: Native Model and Tokenizer Adapter
//
// Role:
// Defines the narrow boundary around one pinned model/tokenizer pair.
//
// Responsibilities:
// - expose reproducibility metadata
// - encode prompts and decode token IDs
// - expose a native forward boundary
//
// Does NOT own:
// - greedy token selection
// - cache policy
// - batching or scheduling
//
// Key invariants:
// - token input is [batch, sequence]
// - logits are [batch, sequence, vocabulary]
// - model loading occurs once per runtime
//
// Evidence required:
// - metadata and shape-contract tests
// - Python/C++ forward parity
//
// Implementation: TODO — Issue #23

#include <cstddef>
#include <string>
#include <vector>

#include "miniserve/runtime/types.hpp"

namespace mlx::core {
class array;
}

namespace miniserve::model {

struct ModelMetadata {
    ModelIdentity identity;
    std::size_t vocabulary_size{};
    std::size_t layer_count{};
    std::size_t attention_head_count{};
    std::size_t kv_head_count{};
    std::size_t head_dimension{};
    std::size_t maximum_context{};
};

class ModelAdapter {
public:
    [[nodiscard]] const ModelMetadata& metadata() const noexcept;
    [[nodiscard]] std::vector<TokenId> encode_prompt(const std::string& prompt) const;
    [[nodiscard]] std::string decode_tokens(const std::vector<TokenId>& tokens) const;
    [[nodiscard]] mlx::core::array forward(const mlx::core::array& token_ids);

    // TODO — Issue #23: choose and document construction, ownership, move, and
    // destruction semantics before adding model/tokenizer state.
};

}  // namespace miniserve::model
