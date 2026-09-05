// MiniServe — Issue #21: C++20 and MLX C++ Runtime Bootstrap
//
// Role:
// Native process entry point. Prints build identity and exits.
//
// Does NOT own model loading, generation, or scheduling.
// Success here means the binary started. It does not mean inference works.

#include "miniserve/runtime/bootstrap.hpp"

#include <iostream>

int main() {
    miniserve::runtime::write_build_identity(std::cout);

    const auto id = miniserve::runtime::current_build_identity();
    if (id.mlx_enabled && !miniserve::runtime::mlx_link_smoke()) {
        std::cerr << "error: MLX C++ was configured but the link smoke test failed\n";
        return 1;
    }
    return 0;
}
