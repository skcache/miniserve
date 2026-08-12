// MiniServe — Issues #26–#28: KV-Cache Contract Tests
//
// Compile-only evidence for capacity and valid-length vocabulary.
// Append, overflow, reset, reuse, and isolation tests remain required by the issues.

#include <cstddef>
#include <type_traits>

#include "miniserve/cache/kv_cache.hpp"

int main() {
    using miniserve::cache::KvCacheShape;
    using miniserve::cache::KvCacheState;

    constexpr KvCacheState empty{{2, 1, 4, 128, 64}, 0};
    static_assert(empty.valid_length == 0);
    static_assert(empty.shape.capacity == 128);
    static_assert(std::is_same_v<decltype(KvCacheShape{}.capacity), std::size_t>);
    return 0;
}
