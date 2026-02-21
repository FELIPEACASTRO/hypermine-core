cmake_minimum_required(VERSION 3.28)
project(hypermine-core
    VERSION 1.0.0
    DESCRIPTION "Universal High-Performance Cryptocurrency Miner"
    LANGUAGES C CXX
)

# ============================================================================
# C++20 Standard
# ============================================================================
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================================
# Build Options
# ============================================================================
option(ENABLE_CUDA    "Enable NVIDIA CUDA support"     ON)
option(ENABLE_OPENCL  "Enable OpenCL support"           ON)
option(ENABLE_FPGA    "Enable FPGA support"             OFF)
option(ENABLE_AVX2    "Enable AVX2 optimizations"       ON)
option(ENABLE_AVX512  "Enable AVX-512 optimizations"    ON)
option(ENABLE_SHANI   "Enable SHA-NI optimizations"     ON)
option(ENABLE_NEON    "Enable ARM NEON optimizations"    OFF)
option(ENABLE_TESTS   "Build test suite"                ON)
option(ENABLE_BENCH   "Build benchmarks"                ON)
option(ENABLE_LTO     "Enable Link-Time Optimization"   ON)
option(ENABLE_PGO     "Enable Profile-Guided Optimization" OFF)

# ============================================================================
# Compiler Detection and Flags
# ============================================================================
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    # Optimization flags
    set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")
    
    # Architecture-specific flags
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
        add_compile_options(-march=native -mtune=native)
        
        if(ENABLE_AVX2)
            add_compile_definitions(HYPERMINE_AVX2)
        endif()
        if(ENABLE_AVX512)
            add_compile_definitions(HYPERMINE_AVX512)
        endif()
        if(ENABLE_SHANI)
            add_compile_definitions(HYPERMINE_SHANI)
        endif()
    elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64|ARM64")
        if(ENABLE_NEON)
            add_compile_definitions(HYPERMINE_NEON)
        endif()
    endif()
    
    # Link-Time Optimization
    if(ENABLE_LTO)
        set(CMAKE_INTERPROCEDURAL_OPTIMIZATION TRUE)
    endif()
    
    # Additional optimization flags
    add_compile_options(
        -funroll-loops
        -fomit-frame-pointer
        -fno-exceptions      # No exceptions in hot path
        -Wall -Wextra -Wpedantic
    )
endif()

# ============================================================================
# CUDA Support
# ============================================================================
if(ENABLE_CUDA)
    enable_language(CUDA)
    find_package(CUDAToolkit REQUIRED)
    
    set(CMAKE_CUDA_STANDARD 20)
    set(CMAKE_CUDA_ARCHITECTURES "60;70;75;80;86;89;90")
    
    add_compile_definitions(HYPERMINE_CUDA)
    
    # CUDA optimization flags
    set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} --use_fast_math")
    set(CMAKE_CUDA_FLAGS_RELEASE "${CMAKE_CUDA_FLAGS_RELEASE} -O3")
endif()

# ============================================================================
# OpenCL Support
# ============================================================================
if(ENABLE_OPENCL)
    find_package(OpenCL REQUIRED)
    add_compile_definitions(HYPERMINE_OPENCL)
endif()

# ============================================================================
# Rust Integration (via corrosion)
# ============================================================================
include(FetchContent)
FetchContent_Declare(
    Corrosion
    GIT_REPOSITORY https://github.com/corrosion-rs/corrosion.git
    GIT_TAG v0.5
)
FetchContent_MakeAvailable(Corrosion)

# Import Rust crates
corrosion_import_crate(MANIFEST_PATH ${CMAKE_SOURCE_DIR}/Cargo.toml)

# ============================================================================
# Dependencies
# ============================================================================
find_package(Threads REQUIRED)
find_package(OpenSSL REQUIRED)

# spdlog for logging
FetchContent_Declare(
    spdlog
    GIT_REPOSITORY https://github.com/gabime/spdlog.git
    GIT_TAG v1.14.1
)
FetchContent_MakeAvailable(spdlog)

# ============================================================================
# Source Files
# ============================================================================

# Core library
add_library(hypermine_core STATIC
    src/core/main.cpp
    src/hardware/hal.cpp
    src/hardware/cpu_backend.cpp
    src/hardware/cpuid.cpp
    src/hardware/gpu_info.cpp
)

target_include_directories(hypermine_core PUBLIC
    ${CMAKE_SOURCE_DIR}/src
)

target_link_libraries(hypermine_core PUBLIC
    Threads::Threads
    OpenSSL::SSL
    OpenSSL::Crypto
    spdlog::spdlog
)

# Algorithm libraries
add_library(hypermine_algorithms STATIC
    src/algorithms/sha256/sha256_generic.cpp
    src/algorithms/sha256/sha256_avx2.cpp
    src/algorithms/sha256/sha256_avx512.cpp
    src/algorithms/sha256/sha256_shani.cpp
    src/algorithms/scrypt/scrypt.cpp
    src/algorithms/ethash/ethash.cpp
    src/algorithms/randomx/randomx.cpp
    src/algorithms/x11/x11.cpp
    src/algorithms/equihash/equihash.cpp
    src/algorithms/ghostrider/ghostrider.cpp
)

target_link_libraries(hypermine_algorithms PUBLIC hypermine_core)

# CUDA kernels
if(ENABLE_CUDA)
    add_library(hypermine_cuda STATIC
        src/hardware/cuda_backend.cu
        src/algorithms/ethash/ethash.cu
        src/algorithms/kawpow/kawpow.cu
        src/algorithms/scrypt/scrypt.cu
        src/algorithms/equihash/equihash.cu
        src/algorithms/autolykos2/autolykos2.cu
    )
    target_link_libraries(hypermine_cuda PUBLIC
        CUDA::cudart
        CUDA::cuda_driver
    )
    target_link_libraries(hypermine_algorithms PUBLIC hypermine_cuda)
endif()

# OpenCL kernels
if(ENABLE_OPENCL)
    add_library(hypermine_opencl STATIC
        src/hardware/opencl_backend.cpp
        src/algorithms/ethash/ethash_cl.cpp
        src/algorithms/kawpow/kawpow_cl.cpp
        src/algorithms/scrypt/scrypt_cl.cpp
        src/algorithms/equihash/equihash_cl.cpp
        src/algorithms/autolykos2/autolykos2_cl.cpp
    )
    target_link_libraries(hypermine_opencl PUBLIC OpenCL::OpenCL)
    target_link_libraries(hypermine_algorithms PUBLIC hypermine_opencl)
endif()

# Main executable
add_executable(hypermine src/core/main.cpp)
target_link_libraries(hypermine PRIVATE
    hypermine_core
    hypermine_algorithms
)

# ============================================================================
# Assembly files (x86-64)
# ============================================================================
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64|AMD64")
    enable_language(ASM_NASM)
    target_sources(hypermine_algorithms PRIVATE
        src/algorithms/sha256/sha256_asm.S
    )
endif()

# ============================================================================
# Tests
# ============================================================================
if(ENABLE_TESTS)
    enable_testing()
    
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG v1.15.2
    )
    FetchContent_MakeAvailable(googletest)
    
    add_executable(hypermine_tests
        tests/test_sha256.cpp
    )
    target_link_libraries(hypermine_tests PRIVATE
        hypermine_algorithms
        GTest::gtest_main
    )
    
    include(GoogleTest)
    gtest_discover_tests(hypermine_tests)
endif()

# ============================================================================
# Benchmarks
# ============================================================================
if(ENABLE_BENCH)
    FetchContent_Declare(
        benchmark
        GIT_REPOSITORY https://github.com/google/benchmark.git
        GIT_TAG v1.9.1
    )
    set(BENCHMARK_ENABLE_TESTING OFF)
    FetchContent_MakeAvailable(benchmark)
    
    add_executable(hypermine_bench
        benchmarks/bench_sha256.cpp
        benchmarks/bench_all.cpp
    )
    target_link_libraries(hypermine_bench PRIVATE
        hypermine_algorithms
        benchmark::benchmark
    )
endif()

# ============================================================================
# Install
# ============================================================================
install(TARGETS hypermine DESTINATION bin)
install(FILES config.toml DESTINATION etc/hypermine)
install(DIRECTORY coins/ DESTINATION etc/hypermine/coins)
