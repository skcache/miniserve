#pragma once

// MiniServe — Issue #21: C++20 and MLX C++ Runtime Bootstrap
//
// Role:
// Reports how this native binary was built. This is the process identity
// surface, not an inference API.
//
// Responsibilities:
// - expose compiler, architecture, and build-type identity
// - say whether MLX C++ was linked at configure time
// - optionally prove that the MLX C++ library can construct a tiny array
//
// Does NOT own:
// - model loading
// - tokenization
// - generation, cache, or scheduling
//
// Key invariants:
// - no machine-local filesystem path is compiled into these strings
// - "MLX linked" is never presented as "inference works"

#include <iosfwd>

namespace miniserve::runtime {

struct BuildIdentity {
    const char* compiler_id;
    const char* compiler_version;
    const char* system_processor;
    const char* build_type;
    bool mlx_enabled;
};

[[nodiscard]] BuildIdentity current_build_identity() noexcept;
[[nodiscard]] bool mlx_link_smoke();
void write_build_identity(std::ostream& out);

}  // namespace miniserve::runtime
