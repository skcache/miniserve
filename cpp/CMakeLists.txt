cmake_minimum_required(VERSION 3.24)

if(APPLE AND NOT CMAKE_OSX_ARCHITECTURES)
    set(CMAKE_OSX_ARCHITECTURES "arm64" CACHE STRING "Apple Silicon")
endif()

project(miniserve_cpp VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(MINISERVE_ENABLE_MLX "Link MLX C++" OFF)
set(MLX_CPP_ROOT "" CACHE PATH "mlx package root (has share/cmake/MLX)")

add_library(miniserve_runtime
    src/benchmarks/measurement.cpp
    src/cache/contiguous_cache.cpp
    src/cache/kv_cache.cpp
    src/cache/naive_cache.cpp
    src/generation/generation.cpp
    src/generation/prefill_decode.cpp
    src/model/adapter.cpp
    src/runtime/parity.cpp
    src/runtime/request.cpp
    src/scheduling/batching.cpp
    src/scheduling/queue.cpp
    src/scheduling/scheduler.cpp
)

target_compile_features(miniserve_runtime PUBLIC cxx_std_20)
target_include_directories(miniserve_runtime PUBLIC include)

if(MINISERVE_ENABLE_MLX)
    set(_mlx_root "${MLX_CPP_ROOT}")
    if(NOT _mlx_root)
        file(GLOB _mlx_root "${CMAKE_CURRENT_SOURCE_DIR}/../.venv/lib/python*/site-packages/mlx")
        if(_mlx_root)
            list(GET _mlx_root 0 _mlx_root)
        endif()
    endif()
    list(PREPEND CMAKE_PREFIX_PATH "${_mlx_root}")
    find_package(MLX CONFIG REQUIRED)
    target_link_libraries(miniserve_runtime PUBLIC mlx)
    if(MLX_LIBRARY_DIRS)
        set(CMAKE_BUILD_RPATH "${MLX_LIBRARY_DIRS}")
    endif()
    target_compile_definitions(miniserve_runtime PUBLIC MINISERVE_HAS_MLX=1)
else()
    target_compile_definitions(miniserve_runtime PUBLIC MINISERVE_HAS_MLX=0)
endif()

add_executable(miniserve_cpp src/main.cpp)
target_link_libraries(miniserve_cpp PRIVATE miniserve_runtime)

include(CTest)
if(BUILD_TESTING)
    foreach(test_name IN ITEMS model cache scheduler generation parity)
        add_executable(test_${test_name} tests/test_${test_name}.cpp)
        target_link_libraries(test_${test_name} PRIVATE miniserve_runtime)
        add_test(NAME ${test_name}_contract COMMAND test_${test_name})
    endforeach()
    add_test(NAME bootstrap COMMAND miniserve_cpp)
endif()
