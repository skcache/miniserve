// MiniServe — Issue #21: C++20 / MLX C++ bootstrap. Not inference.

#include <iostream>

#if MINISERVE_HAS_MLX
#include "mlx/mlx.h"
#endif

int main() {
    std::cout << "miniserve cpp\n";
#if MINISERVE_HAS_MLX
    auto z = mlx::core::array({1, 2}) + mlx::core::array({3, 4});
    mlx::core::eval(z);
    std::cout << "mlx: ok\n";
#else
    std::cout << "mlx: off\n";
#endif
    return 0;
}
