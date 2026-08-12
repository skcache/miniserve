// MiniServe — Issue #21: C++20 and MLX C++ Runtime Bootstrap
//
// Role:
// Provides the native process entry point and reports build capabilities.
//
// Responsibilities:
// - prove the C++20 target starts
// - report whether MLX C++ was configured
// - fail clearly until an inference command is implemented
//
// Does NOT own:
// - model loading
// - generation
// - scheduling
//
// Key invariants:
// - no machine-local paths are compiled into the binary
// - bootstrap success is not presented as inference success
//
// Evidence required:
// - CMake build and CTest smoke run
//
// Implementation: bootstrap only — Issue #21

#include <iostream>

int main() {
    std::cout << "MiniServe C++ V1 scaffold\n";
#if MINISERVE_HAS_MLX
    std::cout << "MLX C++ configuration: enabled\n";
#else
    std::cout << "MLX C++ configuration: disabled (set MINISERVE_ENABLE_MLX=ON)\n";
#endif
    std::cout << "Inference runtime: TODO — begin with Issue #21\n";
    return 0;
}
