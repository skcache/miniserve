cmake_minimum_required(VERSION 3.24)

# MiniServe's first native target is Apple Silicon. Pin arm64 before project()
# so compiler detection matches libmlx from the Python package. Override with
# -DCMAKE_OSX_ARCHITECTURES=... if you are deliberately cross-compiling.
if(APPLE AND NOT CMAKE_OSX_ARCHITECTURES)
    set(CMAKE_OSX_ARCHITECTURES "arm64" CACHE STRING "MiniServe native architecture")
endif()

project(miniserve_cpp VERSION 0.1.0 LANGUAGES CXX)

# C++20 is required for the native runtime. Extensions (gnu++20) are off so
# the dialect matches what later MLX C++ code expects.
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(MINISERVE_ENABLE_MLX "Link the native runtime against MLX C++" OFF)
set(MLX_CPP_ROOT "" CACHE PATH "MLX prefix (package root or classic include/lib prefix)")
set(MINISERVE_PYTHON "" CACHE FILEPATH "Python interpreter used to locate the MLX CMake package")

add_library(miniserve_runtime
    src/benchmarks/measurement.cpp
    src/cache/contiguous_cache.cpp
    src/cache/kv_cache.cpp
    src/cache/naive_cache.cpp
    src/generation/generation.cpp
    src/generation/prefill_decode.cpp
    src/model/adapter.cpp
    src/runtime/bootstrap.cpp
    src/runtime/parity.cpp
    src/runtime/request.cpp
    src/scheduling/batching.cpp
    src/scheduling/queue.cpp
    src/scheduling/scheduler.cpp
)

target_compile_features(miniserve_runtime PUBLIC cxx_std_20)
target_include_directories(miniserve_runtime PUBLIC include)

if(NOT CMAKE_BUILD_TYPE)
    set(_miniserve_build_type "unspecified")
else()
    set(_miniserve_build_type "${CMAKE_BUILD_TYPE}")
endif()

if(CMAKE_OSX_ARCHITECTURES)
    set(_miniserve_arch "${CMAKE_OSX_ARCHITECTURES}")
else()
    set(_miniserve_arch "${CMAKE_SYSTEM_PROCESSOR}")
endif()

target_compile_definitions(miniserve_runtime PUBLIC
    MINISERVE_COMPILER_ID="${CMAKE_CXX_COMPILER_ID}"
    MINISERVE_COMPILER_VERSION="${CMAKE_CXX_COMPILER_VERSION}"
    MINISERVE_SYSTEM_PROCESSOR="${_miniserve_arch}"
    MINISERVE_BUILD_TYPE="${_miniserve_build_type}"
)

function(miniserve_mlx_from_python python_executable out_root)
    set(${out_root} "" PARENT_SCOPE)
    if(NOT python_executable)
        return()
    endif()
    if(NOT EXISTS "${python_executable}")
        return()
    endif()
    # Clear Conda/Anaconda variables so a project .venv interpreter cannot be
    # redirected at an unrelated site-packages tree.
    execute_process(
        COMMAND
            "${CMAKE_COMMAND}" -E env
            --unset=PYTHONHOME
            --unset=PYTHONPATH
            --unset=CONDA_PREFIX
            --unset=CONDA_DEFAULT_ENV
            "${python_executable}" -m mlx --cmake-dir
        RESULT_VARIABLE _mlx_probe_status
        OUTPUT_VARIABLE _mlx_probe_root
        ERROR_VARIABLE _mlx_probe_error
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_STRIP_TRAILING_WHITESPACE
    )
    if(_mlx_probe_status EQUAL 0 AND IS_DIRECTORY "${_mlx_probe_root}")
        set(${out_root} "${_mlx_probe_root}" PARENT_SCOPE)
    else()
        message(STATUS "MiniServe MLX C++: skipped Python ${python_executable} (status=${_mlx_probe_status})")
        if(_mlx_probe_error)
            message(STATUS "  ${_mlx_probe_error}")
        endif()
    endif()
endfunction()

function(miniserve_try_enable_mlx mlx_root)
    set(MINISERVE_MLX_LINKED FALSE PARENT_SCOPE)

    if(EXISTS "${mlx_root}/share/cmake/MLX/MLXConfig.cmake")
        list(PREPEND CMAKE_PREFIX_PATH "${mlx_root}")
        find_package(MLX CONFIG REQUIRED)
        target_link_libraries(miniserve_runtime PUBLIC mlx)
        if(MLX_CXX_FLAGS)
            target_compile_options(miniserve_runtime PUBLIC ${MLX_CXX_FLAGS})
        endif()
        if(MLX_LIBRARY_DIRS)
            set(CMAKE_BUILD_RPATH "${MLX_LIBRARY_DIRS}" PARENT_SCOPE)
            set(CMAKE_INSTALL_RPATH "${MLX_LIBRARY_DIRS}" PARENT_SCOPE)
        endif()
        set(MINISERVE_MLX_LINKED TRUE PARENT_SCOPE)
        message(STATUS "MiniServe MLX C++: enabled via MLXConfig.cmake")
        message(STATUS "  root: ${mlx_root}")
        return()
    endif()

    find_path(MLX_CPP_INCLUDE_DIR
        NAMES mlx/array.h
        HINTS "${mlx_root}"
        PATH_SUFFIXES include
    )
    find_library(MLX_CPP_LIBRARY
        NAMES mlx
        HINTS "${mlx_root}"
        PATH_SUFFIXES lib
    )
    if(MLX_CPP_INCLUDE_DIR AND MLX_CPP_LIBRARY)
        target_include_directories(miniserve_runtime PUBLIC "${MLX_CPP_INCLUDE_DIR}")
        target_link_libraries(miniserve_runtime PUBLIC "${MLX_CPP_LIBRARY}")
        get_filename_component(_mlx_lib_dir "${MLX_CPP_LIBRARY}" DIRECTORY)
        set(CMAKE_BUILD_RPATH "${_mlx_lib_dir}" PARENT_SCOPE)
        set(CMAKE_INSTALL_RPATH "${_mlx_lib_dir}" PARENT_SCOPE)
        set(MINISERVE_MLX_LINKED TRUE PARENT_SCOPE)
        message(STATUS "MiniServe MLX C++: enabled via include/library search")
        message(STATUS "  include: ${MLX_CPP_INCLUDE_DIR}")
        message(STATUS "  library: ${MLX_CPP_LIBRARY}")
        return()
    endif()
endfunction()

if(MINISERVE_ENABLE_MLX)
    set(_miniserve_mlx_root "")

    if(MLX_CPP_ROOT)
        set(_miniserve_mlx_root "${MLX_CPP_ROOT}")
        message(STATUS "MiniServe MLX C++: using MLX_CPP_ROOT=${MLX_CPP_ROOT}")
    else()
        get_filename_component(_miniserve_repo_root "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
        file(GLOB _venv_mlx_configs
            "${_miniserve_repo_root}/.venv/lib/python*/site-packages/mlx/share/cmake/MLX/MLXConfig.cmake"
        )
        if(_venv_mlx_configs)
            list(GET _venv_mlx_configs 0 _venv_mlx_config)
            get_filename_component(_mlx_cmake_dir "${_venv_mlx_config}" DIRECTORY)
            get_filename_component(_mlx_cmake_dir "${_mlx_cmake_dir}" DIRECTORY)
            get_filename_component(_mlx_share_dir "${_mlx_cmake_dir}" DIRECTORY)
            get_filename_component(_miniserve_mlx_root "${_mlx_share_dir}" DIRECTORY)
            message(STATUS "MiniServe MLX C++: found project venv package at ${_miniserve_mlx_root}")
        endif()

        if(NOT _miniserve_mlx_root)
            set(_python_candidates "")
            if(MINISERVE_PYTHON)
                list(APPEND _python_candidates "${MINISERVE_PYTHON}")
            endif()
            list(APPEND _python_candidates
                "${_miniserve_repo_root}/.venv/bin/python"
                "${_miniserve_repo_root}/.venv/bin/python3"
            )
            if(DEFINED Python_EXECUTABLE AND Python_EXECUTABLE)
                list(APPEND _python_candidates "${Python_EXECUTABLE}")
            endif()

            foreach(_python IN LISTS _python_candidates)
                miniserve_mlx_from_python("${_python}" _probed_root)
                if(_probed_root)
                    set(_miniserve_mlx_root "${_probed_root}")
                    message(STATUS "MiniServe MLX C++: discovered via ${_python}")
                    break()
                endif()
            endforeach()
        endif()
    endif()

    if(NOT _miniserve_mlx_root)
        find_package(Python 3.9 COMPONENTS Interpreter QUIET)
        if(Python_EXECUTABLE)
            miniserve_mlx_from_python("${Python_EXECUTABLE}" _probed_root)
            if(_probed_root)
                set(_miniserve_mlx_root "${_probed_root}")
                message(WARNING "MiniServe MLX C++: using ${Python_EXECUTABLE}, which may not be the project .venv. Prefer `uv sync` or -DMLX_CPP_ROOT=...")
            endif()
        endif()
    endif()

    if(_miniserve_mlx_root)
        miniserve_try_enable_mlx("${_miniserve_mlx_root}")
    endif()

    if(NOT MINISERVE_MLX_LINKED)
        message(FATAL_ERROR
            "MINISERVE_ENABLE_MLX=ON but MLX C++ was not found.\n"
            "MiniServe looks for headers (mlx/array.h), libmlx, and preferably MLXConfig.cmake.\n"
            "Tried MLX_CPP_ROOT='${MLX_CPP_ROOT}'.\n"
            "Fix by installing the project Python environment (uv sync) so `python -m mlx --cmake-dir` works,\n"
            "or pass an explicit prefix:\n"
            "  cmake -S cpp -B cpp/build-mlx -DMINISERVE_ENABLE_MLX=ON -DMLX_CPP_ROOT=/path/to/mlx\n"
            "That path is a configure-time argument. Do not commit a machine-local value."
        )
    endif()

    target_compile_definitions(miniserve_runtime PUBLIC MINISERVE_HAS_MLX=1)
    message(STATUS "MiniServe inference runtime: not implemented (bootstrap only)")
else()
    target_compile_definitions(miniserve_runtime PUBLIC MINISERVE_HAS_MLX=0)
    message(STATUS "MiniServe MLX C++: disabled (configure with -DMINISERVE_ENABLE_MLX=ON)")
endif()

add_executable(miniserve_cpp src/main.cpp)
target_link_libraries(miniserve_cpp PRIVATE miniserve_runtime)

include(CTest)
if(BUILD_TESTING)
    foreach(test_name IN ITEMS bootstrap model cache scheduler generation parity)
        add_executable(test_${test_name} tests/test_${test_name}.cpp)
        target_link_libraries(test_${test_name} PRIVATE miniserve_runtime)
        add_test(NAME ${test_name}_contract COMMAND test_${test_name})
    endforeach()

    add_test(NAME bootstrap_identity COMMAND miniserve_cpp)
    set_tests_properties(bootstrap_identity PROPERTIES
        PASS_REGULAR_EXPRESSION "inference_runtime: not implemented"
    )
endif()
