// MiniServe — Issue #21: C++20 and MLX C++ Runtime Bootstrap
//
// Implementation notes for learners:
// - The MINISERVE_* macros are injected by CMake at compile time.
// - They describe the compiler that built this file, not the Python runtime.
// - mlx_link_smoke() is a link/runtime check for libmlx. It is not a model.

#include "miniserve/runtime/bootstrap.hpp"

#include <iostream>

#if MINISERVE_HAS_MLX
#include "mlx/mlx.h"
#endif

#ifndef MINISERVE_COMPILER_ID
#define MINISERVE_COMPILER_ID "unknown"
#endif
#ifndef MINISERVE_COMPILER_VERSION
#define MINISERVE_COMPILER_VERSION "unknown"
#endif
#ifndef MINISERVE_SYSTEM_PROCESSOR
#define MINISERVE_SYSTEM_PROCESSOR "unknown"
#endif
#ifndef MINISERVE_BUILD_TYPE
#define MINISERVE_BUILD_TYPE "unspecified"
#endif

namespace miniserve::runtime {

BuildIdentity current_build_identity() noexcept {
    return BuildIdentity{
        MINISERVE_COMPILER_ID,
        MINISERVE_COMPILER_VERSION,
        MINISERVE_SYSTEM_PROCESSOR,
        MINISERVE_BUILD_TYPE,
#if MINISERVE_HAS_MLX
        true,
#else
        false,
#endif
    };
}

bool mlx_link_smoke() {
#if MINISERVE_HAS_MLX
    namespace mx = mlx::core;
    auto x = mx::array({1, 2, 3});
    auto y = mx::array({10, 20, 30});
    auto z = x + y;
    mx::eval(z);
    return z.size() == 3;
#else
    return false;
#endif
}

void write_build_identity(std::ostream& out) {
    const auto id = current_build_identity();
    out << "MiniServe C++ V1 bootstrap\n";
    out << "compiler: " << id.compiler_id << " " << id.compiler_version << "\n";
    out << "architecture: " << id.system_processor << "\n";
    out << "build_type: " << id.build_type << "\n";
    out << "cxx_standard: 20\n";
    if (id.mlx_enabled) {
        out << "mlx_cpp: enabled\n";
        out << "mlx_link_smoke: " << (mlx_link_smoke() ? "ok" : "failed") << "\n";
    } else {
        out << "mlx_cpp: disabled (configure with -DMINISERVE_ENABLE_MLX=ON)\n";
    }
    out << "inference_runtime: not implemented\n";
}

}  // namespace miniserve::runtime
