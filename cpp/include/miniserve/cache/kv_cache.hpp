#pragma once

// MiniServe — Issue #26: KV-Cache Interface and Ownership
//
// Role:
// Defines cache shape and lifetime invariants before storage is implemented.
//
// Responsibilities:
// - distinguish capacity from valid length
// - describe per-layer K/V dimensions
// - expose bounds and reset contracts
//
// Does NOT own:
// - model weights
// - request scheduling
// - token selection
//
// Key invariants:
// - writes never exceed capacity
// - state cannot alias across unrelated requests
// - valid length excludes uninitialized storage
//
// Evidence required:
// - shape, bounds, reset, and isolation tests
//
// Implementation: TODO — Issue #26

#include <cstddef>

namespace miniserve::cache {

struct KvCacheShape {
    std::size_t layer_count{};
    std::size_t batch_size{};
    std::size_t kv_head_count{};
    std::size_t capacity{};
    std::size_t head_dimension{};
};

struct KvCacheState {
    KvCacheShape shape;
    std::size_t valid_length{};
};

class KvCache;

}  // namespace miniserve::cache
