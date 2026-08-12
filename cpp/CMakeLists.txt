cmake_minimum_required(VERSION 3.24)

project(miniserve_cpp VERSION 0.1.0 LANGUAGES CXX)

option(MINISERVE_ENABLE_MLX "Configure the scaffold against a local MLX C++ build" OFF)
set(MLX_CPP_ROOT "" CACHE PATH "Prefix containing MLX C++ headers and libraries")

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
    find_path(MLX_CPP_INCLUDE_DIR
        NAMES mlx/array.h
        HINTS "${MLX_CPP_ROOT}"
        PATH_SUFFIXES include
        REQUIRED
    )
    find_library(MLX_CPP_LIBRARY
        NAMES mlx
        HINTS "${MLX_CPP_ROOT}"
        PATH_SUFFIXES lib
        REQUIRED
    )
    target_include_directories(miniserve_runtime PUBLIC "${MLX_CPP_INCLUDE_DIR}")
    target_link_libraries(miniserve_runtime PUBLIC "${MLX_CPP_LIBRARY}")
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
endif()
