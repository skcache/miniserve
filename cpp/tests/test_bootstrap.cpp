// MiniServe — Issue #21: Bootstrap identity tests
//
// These assert process identity, not model behavior.

#include "miniserve/runtime/bootstrap.hpp"

#include <cstring>
#include <sstream>
#include <string>

int main() {
    const auto id = miniserve::runtime::current_build_identity();
    if (id.compiler_id == nullptr || std::strlen(id.compiler_id) == 0) {
        return 1;
    }
    if (id.compiler_version == nullptr || std::strlen(id.compiler_version) == 0) {
        return 2;
    }
    if (id.system_processor == nullptr || std::strlen(id.system_processor) == 0) {
        return 3;
    }
    if (id.build_type == nullptr || std::strlen(id.build_type) == 0) {
        return 4;
    }

#if MINISERVE_HAS_MLX
    if (!id.mlx_enabled) {
        return 5;
    }
    if (!miniserve::runtime::mlx_link_smoke()) {
        return 6;
    }
#else
    if (id.mlx_enabled) {
        return 7;
    }
    if (miniserve::runtime::mlx_link_smoke()) {
        return 8;
    }
#endif

    std::ostringstream stream;
    miniserve::runtime::write_build_identity(stream);
    const std::string text = stream.str();
    if (text.find("MiniServe C++ V1 bootstrap") == std::string::npos) {
        return 9;
    }
    if (text.find("inference_runtime: not implemented") == std::string::npos) {
        return 10;
    }
    if (text.find("cxx_standard: 20") == std::string::npos) {
        return 11;
    }

#if MINISERVE_HAS_MLX
    if (text.find("mlx_cpp: enabled") == std::string::npos) {
        return 12;
    }
#else
    if (text.find("mlx_cpp: disabled") == std::string::npos) {
        return 13;
    }
#endif

    return 0;
}
